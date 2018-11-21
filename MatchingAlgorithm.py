import pandas as pd

# Distribution of points for the runtime comparison
RUNTIME_DIST = {"1": 100, "2": 92.1, "3": 82.7, "4": 71.2, "5": 56.5, "6": 35.6, "7": 0}

# Distribution of points for the budget comparison
BUDGET_DIST = {"1": 100, "2": 89.8, "3": 77.4, "4": 61.3, "5": 38.7, "6": 0}

#DIRECTOR_DIST = {"1": 100, "2": 85, "3": 70, "4": 50, "5": 30, "6": 15, "7": 10, "8": 5, "9": 0}
DIRECTOR_DIST = {"1": 100, "2": 0}

ACTOR_DIST = {"1": 100, "2": 89.842, "3": 77.371, "4": 61.315, "5": 38.685, "6": 0}

COMPANIES_DIST = {"1": 100, "2": 79.248, "3": 50, "4": 0}

COMPANY_CLOSE_MATCH_REDUCTION = 0.5 #Reduce distance by 50%

BUDGET_WEIGHT = 5000
RUNTIME_WEIGHT = 1000
DIRECTOR_WEIGHT = 1000
GENRE_WEIGHT = 1000
ACTOR_WEIGHT = 5000
COMPANIES_WEIGHT = 5000
VOTE_COUNT_WEIGHT = 1000

NUM_CANDIDATES = 20  # The number of candidates to keep track of

#List of boolean, in same order as companies given, to see if close match is required
predictCompaniesCloseMatchBooleanList = []

def runAlgorithm():

    dataSetDF = pd.read_csv('tmbdWithPoints.csv', dtype='object')
    dataFrame = pd.read_csv('toPredict.csv', dtype='object', error_bad_lines=False)

    for dfToPredict in dataFrame.iterrows():
        print("*******************************************************************************************************")
    # dfToPredict = pd.read_csv('toPredict.csv', dtype='object').iloc[0]
        dfToPredict = dfToPredict[1]
        checkIfCompaniesCloseMatchesNeeded(dfToPredict, dataSetDF)

        topCandidates = []

        for i in range(NUM_CANDIDATES):
            topCandidates.append((0, None))

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

    revPrediction = 0
    ratingPrediction = 0
    numberOfRatings = 0
    totalPoints = 0

    for candidate in candidateList:
        if int(candidate[1]['revenue']) > 0:
            revPrediction += int(candidate[1]['revenue']) * int(candidate[0])
            totalPoints += candidate[0]
            ratingPrediction += float(candidate[1]['vote_average']) * float(candidate[1]['vote_count']) * float(candidate[0])
            numberOfRatings += float(candidate[1]['vote_count']) * float(candidate[0])

    print(str(revPrediction))
    print(ratingPrediction)
    print("\nRevenue Prediction: " + str(revPrediction / (NUM_CANDIDATES * totalPoints)))
    print("\nRating Prediction: " + str(ratingPrediction / numberOfRatings ))


def calculateDistance(toPredict, toCompare):

    totalDist = 0

    runtimeDist = matchRuntime(toPredict['runtime'], toCompare['runtime'])
    budgetDist = matchBudget(toPredict['budget'], toCompare['budget'])
    directorDist = matchDirector(toPredict['director'], toCompare['director'])
    genreDist = matchGenres(toPredict['genres'], toCompare['genres'])
    actorDist = matchActors(toPredict['cast'], toCompare['cast'])
    companyDist = matchCompanies(toPredict['production_companies'], toCompare['production_companies'])
    voteCountDis = evaluateVoteCount(toCompare)

    totalDist += runtimeDist * RUNTIME_WEIGHT
    totalDist += budgetDist * BUDGET_WEIGHT
    totalDist += directorDist * DIRECTOR_WEIGHT
    totalDist += genreDist * GENRE_WEIGHT
    totalDist += actorDist * ACTOR_WEIGHT
    totalDist += companyDist * COMPANIES_WEIGHT
    totalDist += voteCountDis * VOTE_COUNT_WEIGHT

    return totalDist


def evaluateVoteCount(toCompare):
    weight = 0
    if int(toCompare['vote_count']) >= 5000:
        weight = 100
    elif 3000 <= int(toCompare['vote_count']) < 5000:
        weight = 80
    elif 2000 <= int(toCompare['vote_count']) < 3000:
        weight = 60
    elif 1000 <= int(toCompare['vote_count']) < 2000:
        weight = 40
    elif 500 <= int(toCompare['vote_count']) < 1000:
        weight = 20
    else:
        weight = 0
    return weight


def matchGenres(toPredictGenresString, toCompareGenresString):
    toPredictGenres = str(toPredictGenresString).split("|")
    toCompareGenres = str(toCompareGenresString).split("|")

    toCompareGenresSet = set(toCompareGenres)

    commonCount = 0

    for genre in toPredictGenres:
        if genre in toCompareGenresSet:
            commonCount += 1

    return 100 * commonCount/len(toPredictGenres)


def matchRuntime(toPredictRuntime, toCompareRuntime):
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


def matchBudget(toPredictBudget, toCompareBudget):
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

def matchActors(toPredictActors, toCompareActors):
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

def matchCompanies(toPredictCompanies, toCompareCompanies):
    toPredictCompanies = str(toPredictCompanies).split("|")
    toCompareCompanies = str(toCompareCompanies).split("|")

    toPredictCompaniesList = []
    toCompareCompaniesList = []

    for i in toPredictCompanies:
        toPredictCompaniesList.append(i.split(":")[0])

    for j in toCompareCompanies:
        toCompareCompaniesList.append(j.split(":")[0])

    toCompareCompaniesSet = set(toCompareCompaniesList)

    commonCount = 0.0

    for company in toPredictCompaniesList:
        companyIndex = toPredictCompaniesList.index(company)

        if (predictCompaniesCloseMatchBooleanList[companyIndex] == True):
            companyWordsSplit = str(company).split(" ")
            companyWordsSplitIndex = len(companyWordsSplit)

            for index in range(1,companyWordsSplitIndex):
                likeCompany = " ".join(companyWordsSplit[:-index])

                if likeCompany in toCompareCompaniesSet:
                    commonCount += COMPANY_CLOSE_MATCH_REDUCTION
                    break
        else:
            if company in toCompareCompaniesSet:
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

    # if commonCount > 1:
    #     print(distance)
#        print("\nCompanies: " + toCompareCompanies)

    return distance

def checkIfCompaniesCloseMatchesNeeded(dfToPredict,dataSetDF):
    print(str(dfToPredict[0]))
    toPredictCompanies = str(dfToPredict['production_companies']).split("|")

    for company in toPredictCompanies:
        companyMatches = dataSetDF.loc[dataSetDF['production_companies'] == company]

        if (companyMatches.empty):
            predictCompaniesCloseMatchBooleanList.append(True)
        else:
            predictCompaniesCloseMatchBooleanList.append(False)


def matchDirector(toPredictDirector, toCompareDirector):

    if str(toPredictDirector) in str(toCompareDirector):
        distance = DIRECTOR_DIST.get("1")
    else:
        distance = DIRECTOR_DIST.get("2")

    return distance


def compareDirectorPoints(toPredictDirector, toCompareDirector):
    points = -1

    #if match,but without points = 0; no match points = -1,
    if str(toPredictDirector) in str(toCompareDirector):
        for multiDirectors in str(toCompareDirector).split("|"):
             if str(toPredictDirector) in multiDirectors:
                 if "points" in multiDirectors:
                     pointsIndexStart = multiDirectors.find(":")
                     pointsIndexEnd = multiDirectors.find("points")
                     points = int(multiDirectors[pointsIndexStart + 1:pointsIndexEnd - 1])
                 else:
                     points = 0

    if points > 50000:
        distance = DIRECTOR_DIST.get("1")
    elif 20000 < points <= 50000:
        distance = DIRECTOR_DIST.get("2")
    elif 10000 < points <= 20000:
        distance = DIRECTOR_DIST.get("3")
    elif 5000 < points <= 10000:
        distance = DIRECTOR_DIST.get("4")
    elif 2000 < points <= 5000:
        distance = DIRECTOR_DIST.get("5")
    elif 1000 < points <= 2000:
        distance = DIRECTOR_DIST.get("6")
    elif 0 < points <= 1000:
        distance = DIRECTOR_DIST.get("7")
    elif points == 0:
        distance = DIRECTOR_DIST.get("8")
    else:
        distance = DIRECTOR_DIST.get("9")

    return distance

runAlgorithm()

# Test compareGenres()
# toPredict = "Science Fiction|Fantasy|Action|Adventure|Drama|Horror"
# toCompare = "Action|Adventure|Fantasy|Science Fiction"
# result = compareGenres(toPredict, toCompare)
# print("**** " + str(result))