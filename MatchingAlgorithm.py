import pandas as pd

# Distribution of points for the runtime comparison
RUNTIME_DIST = {"1": 100, "2": 92.1, "3": 82.7, "4": 71.2, "5": 56.5, "6": 35.6, "7": 0}

# Distribution of points for the budget comparison
BUDGET_DIST = {"1": 100, "2": 89.8, "3": 77.4, "4": 61.3, "5": 38.7, "6": 0}

DIRECTOR_DIST = {"1": 100, "2": 0}

ACTOR_DIST = {"1": 100, "2": 89.842, "3": 77.371, "4": 61.315, "5": 38.685, "6": 0}

COMPANIES_DIST = {"1": 100, "2": 79.248, "3": 50, "4": 0}

BUDGET_WEIGHT = 1000
RUNTIME_WEIGHT = 1000
DIRECTOR_WEIGHT = 1000
GENRE_WEIGHT = 1000
ACTOR_WEIGHT = 1000
COMPANIES_WEIGHT = 1000

NUM_CANDIDATES = 20  # The number of candidates to keep track of

def runAlgorithm():

    dataSetDF = pd.read_csv('tmbdWithPoints.csv', dtype='object')
    dfToPredict = pd.read_csv('toPredict.csv', dtype='object').iloc[0]

    topCandidates = []

    for i in range(NUM_CANDIDATES):
        topCandidates.append((0, None))

    print(len(topCandidates))

    for index, row in dataSetDF.iterrows():  # Iterate all rows in our data-set

        currentDist = calculateDistance(dfToPredict, row)

        if currentDist > topCandidates[NUM_CANDIDATES - 1][0]:
            topCandidates[NUM_CANDIDATES - 1] = (currentDist, row)
            topCandidates = sorted(topCandidates, key=lambda x: x[0], reverse=True)

    for i in range(NUM_CANDIDATES):
        print("\nCandidate " + str(i + 1) + " Points: " + str(topCandidates[i][0]) + "   \n" + str(topCandidates[i][1]))

    # Make the prediction based on the top candidates found
    makePrediction(topCandidates)


def makePrediction(candidateList):
    None


def calculateDistance(toPredict, toCompare):

    totalDist = 0

    runtimeDist = compareRuntime(toPredict['runtime'], toCompare['runtime'])
    budgetDist = compareBudget(toPredict['budget'], toCompare['budget'])
    directorDist = compareDirector(toPredict['director'], toCompare['director'])
    genreDist = compareGenres(toPredict['genres'], toCompare['genres'])
    actorDist = compareActors(toPredict['cast'], toCompare['cast'])
    companyDist = compareCompanies(toPredict['production_companies'], toCompare['production_companies'])

    totalDist += runtimeDist * RUNTIME_WEIGHT
    totalDist += budgetDist * BUDGET_WEIGHT
    totalDist += directorDist * DIRECTOR_WEIGHT
    totalDist += genreDist * GENRE_WEIGHT
    totalDist += actorDist * ACTOR_WEIGHT
    totalDist += companyDist * COMPANIES_WEIGHT

    return totalDist


def compareGenres(toPredictGenresString, toCompareGenresString):
    toPredictGenres = str(toPredictGenresString).split("|")
    toCompareGenres = str(toCompareGenresString).split("|")

    toCompareGenresSet = set(toCompareGenres)

    commonCount = 0

    for genre in toPredictGenres:
        if genre in toCompareGenresSet:
            commonCount += 1

    return 100 * commonCount/len(toPredictGenres)


def compareRuntime(toPredictRuntime, toCompareRuntime):
    diff = abs(int(toPredictRuntime) - int(toCompareRuntime))

    if diff <= 5:
        distance = RUNTIME_DIST.get("1")
    elif diff <= 10:
        distance = RUNTIME_DIST.get("2")
    elif diff <= 15:
        distance = RUNTIME_DIST.get("3")
    elif diff <= 20:
        distance = RUNTIME_DIST.get("4")
    elif diff <= 25:
        distance = RUNTIME_DIST.get("5")
    elif diff <= 30:
        distance = RUNTIME_DIST.get("6")
    else:
        distance = RUNTIME_DIST.get("7")

    return distance


def compareBudget(toPredictBudget, toCompareBudget):
    diff = abs(int(toPredictBudget) - int(toCompareBudget)) / int(toPredictBudget) * 100

    if diff <= 5:
        distance = BUDGET_DIST.get("1")
    elif diff <= 10:
        distance = BUDGET_DIST.get("2")
    elif diff <= 15:
        distance = BUDGET_DIST.get("3")
    elif diff <= 20:
        distance = BUDGET_DIST.get("4")
    elif diff <= 25:
        distance = BUDGET_DIST.get("5")
    else:
        distance = BUDGET_DIST.get("6")

    return distance

def compareActors(toPredictActors, toCompareActors):
    toPredictActors = str(toPredictActors).split("|")
    toCompareActors = str(toCompareActors).split("|")

    toPredictActorsList = []
    toCompareActorsList = []

    for i in toPredictActors:
        toPredictActorsList.append(i.split(":")[0])

    for j in toCompareActors:
        toCompareActorsList.append(j.split(":")[0])

    toCompareActorsSet = set(toCompareActorsList)

    commonCount = 0

    for actor in toPredictActorsList:
        if actor in toCompareActorsSet:
            commonCount += 1

    distance = 0

    if commonCount >= 5:
        distance = ACTOR_DIST.get("1")
    elif commonCount == 4:
        distance = ACTOR_DIST.get("2")
    elif commonCount == 3:
        distance = ACTOR_DIST.get("3")
    elif commonCount == 2:
        distance = ACTOR_DIST.get("4")
    elif commonCount == 1:
        distance = ACTOR_DIST.get("5")
    else:
        distance = ACTOR_DIST.get("6")

    return distance

def compareCompanies(toPredictCompanies, toCompareCompanies):
    toPredictCompanies = str(toPredictCompanies).split("|")
    toCompareCompanies = str(toCompareCompanies).split("|")

    toPredictCompaniesList = []
    toCompareCompaniesList = []

    for i in toPredictCompanies:
        toPredictCompaniesList.append(i.split(":")[0])

    for j in toCompareCompanies:
        toCompareCompaniesList.append(j.split(":")[0])

    toCompareCompaniesSet = set(toCompareCompaniesList)

    commonCount = 0

    for actor in toPredictCompaniesList:
        if actor in toCompareCompaniesSet:
            commonCount += 1

    distance = 0

    if commonCount >= 3:
        distance = COMPANIES_DIST.get("1")
    elif commonCount == 2:
        distance = COMPANIES_DIST.get("2")
    elif commonCount == 1:
        distance = COMPANIES_DIST.get("3")
    else:
        distance = COMPANIES_DIST.get("4")

    return distance

def compareDirector(toPredictDirector, toCompareDirector):

    if str(toPredictDirector) in str(toCompareDirector):
        distance = DIRECTOR_DIST.get("1")
    else:
        distance = DIRECTOR_DIST.get("2")

    return distance


runAlgorithm()

# Test compareGenres()
# toPredict = "Science Fiction|Fantasy|Action|Adventure|Drama|Horror"
# toCompare = "Action|Adventure|Fantasy|Science Fiction"
# result = compareGenres(toPredict, toCompare)
# print("**** " + str(result))