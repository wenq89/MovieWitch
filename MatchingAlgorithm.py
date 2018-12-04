import pandas as pd
import numpy as np

# Distribution of points for the runtime comparison
RUNTIME_DIST = {"1": 100, "2": 92.1, "3": 82.7, "4": 71.2, "5": 56.5, "6": 35.6, "7": 0}

# Distribution of points for the budget comparison
BUDGET_DIST = {"1": 100, "2": 89.8, "3": 77.4, "4": 61.3, "5": 38.7, "6": 0}

DIRECTOR_POINTS_DIST = {"1": 100, "2": 85, "3": 70, "4": 50, "5": 30, "6": 15, "7": 10, "8": 5, "9": 0}

DIRECTOR_DIST = {"1": 100, "2": 0}

ACTOR_POINTS_DIST = {"1": 100, "2": 85, "3": 70, "4": 50, "5": 30, "6": 10, "7": 5, "8": 0}
ACTOR_DIST = {"1": 100, "2": 89.8, "3": 77.4, "4": 61.3, "5": 38.7, "6": 0}

COMPANIES_DIST = {"1": 100, "2": 79.2, "3": 50, "4": 0}

# Ratings Variables
#Weights used to match closeness of candidates
BUDGET_WEIGHT = 1 #rating:1, revenue:5
RUNTIME_WEIGHT = 1 #rating:1, revenue:1
DIRECTOR_WEIGHT = 5 #rating:5, revenue:20
GENRE_WEIGHT = 2 #rating:2, revenue:0
ACTOR_WEIGHT = 7 #rating:7, revenue:10
COMPANIES_WEIGHT = 1 #rating:1, revenue:30

#Weights used to make the prediciton based off of the candidates
PREDICTION_ACTOR_WEIGHT = 3 #rating:3, revenue:100
PREDICTION_DIRECTOR_WEIGHT = 4 #rating:4, revenue:50
PREDICTION_MATCHPOINTS_WEIGHT = 5 #rating:5, revenue:10
PREDICTION_VOTECOUNT_WEIGHT = 3 #rating:3, revenue:1

# The number of candidates to keep track of
NUM_CANDIDATES = 13 #rating:13, revenue:4

# if true, gets rating predictions
# if false, gets revenue predictions
FOR_RATING = True

withinFive = []
withinTen = []
withinFifteen = []
withinTwenty = []
withinThirty = []

#List of boolean, in same order as companies given, to see if close match is required
predictCompaniesCloseMatchBooleanList = []

def runAlgorithm():

    dataSetDF = pd.read_csv('tmbdWithPointsV2.csv', dtype='object')
    dataFrame = pd.read_csv('toPredict.csv', dtype='object', error_bad_lines=False)

    for dfToPredict in dataFrame.iterrows():
        print("*******************************************************************************************************")
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

        # Make the prediction based on the top candidates found
        makePrediction(dfToPredict,topCandidates)

    print()
    print("Within 5%: " + str(len(withinFive)))
    print("Within 10%: " + str(len(withinTen)))
    print("Within 15%: " + str(len(withinFifteen)))
    print("Within 20%: " + str(len(withinTwenty)))
    print("Within 30%: " + str(len(withinThirty)))

def makePrediction(toPredict,candidateList):
    print("Predicting for: " + toPredict['title'])
    # print("Candidates: " + str(candidateList))

    if FOR_RATING:
        actualRating = float(toPredict['actual_imdb_rating'])
        predictedRating = predictRating(toPredict, candidateList)
        print("Predicted rating: " + str(predictedRating) + " Actual Rating: " + str(actualRating))
        percentDiff = round((actualRating - predictedRating) / actualRating * 100, 2)
    else:
        actualRevenue = int(toPredict['actual_revenue'])
        predictedRevenue = predictRevenue(toPredict,candidateList)
        print(str("Predicted revenue: " + str(predictedRevenue) + " Actual Revenue: " + str(actualRevenue)))
        print("Difference in revenue prediction: " + str(round((actualRevenue - predictedRevenue) / actualRevenue * 100, 2)) + "%")
        percentDiff = round((actualRevenue - predictedRevenue) / actualRevenue * 100, 2)

    if (abs(percentDiff) <= 5):
        withinFive.append(0)

    if (abs(percentDiff) <= 10):
        withinTen.append(0)

    if (abs(percentDiff) <= 15):
        withinFifteen.append(0)

    if (abs(percentDiff) <= 20):
        withinTwenty.append(0)

    if (abs(percentDiff) <= 30):
        withinThirty.append(0)

    print("Difference in rating prediction: " + str(percentDiff) + "%")

def predictRevenue(toPredict, candidateList):

    revenueRelevantCandidates = []

    #Remove candidates with revenue of 0 where there is not data on the revenue
    for candidate in candidateList:

        currentCandidate = candidate[1]

        if int(currentCandidate['revenue_adj']) > 0:
            revenueRelevantCandidates.append((float(currentCandidate['revenue_adj']), candidate))

    #Calculate the mean and standard deviation of the candidates revenue
    revenueMean = np.mean([x[0] for x in revenueRelevantCandidates])
    revenueSD = np.std([x[0] for x in revenueRelevantCandidates])

    #Remove outliers from the candidates
    finalRevenues = [x for x in revenueRelevantCandidates if (float(x[0]) < revenueMean + 3 * revenueSD)]
    finalRevenues = [x for x in finalRevenues if (float(x[0]) > revenueMean - 0.25 * revenueSD)]


    #Add the weights for each of the remaining candidates
    finalRevenueCandidatesWithWeight = []

    for candidate in finalRevenues:
        directorPoints = compareDirectorPoints(toPredict['director'], candidate[1][1]['director'])
        actorPoints = compareActorPoints(toPredict['cast'], candidate[1][1]['cast'])
        matchPoints = candidate[1][0] / np.max([float(x[1][0]) for x in finalRevenues]) * 100
        candidateWeight = PREDICTION_MATCHPOINTS_WEIGHT * matchPoints \
                          + PREDICTION_ACTOR_WEIGHT * actorPoints \
                          + PREDICTION_DIRECTOR_WEIGHT * directorPoints
        finalRevenueCandidatesWithWeight.append((candidateWeight, candidate[0]))

    #Calculate the prediction
    sumRevenueCandidateWeights = np.sum([float(x[0]) for x in finalRevenueCandidatesWithWeight])
    sumRevenueTimesCandidateWeight = np.sum([float(x[0]) * float(x[1]) for x in finalRevenueCandidatesWithWeight])

    revenuePrediction = float(sumRevenueTimesCandidateWeight / sumRevenueCandidateWeights)

    return revenuePrediction

def predictRating(toPredict, candidateList):

    ratingRelevantCandidates = []

    for candidate in candidateList:

        currentCandidate = candidate[1]

        if float(currentCandidate['vote_avg']) > 0:
            ratingRelevantCandidates.append((float(currentCandidate['vote_avg']), candidate))

    ratingMean = np.mean([x[0] for x in ratingRelevantCandidates])
    ratingSD = np.std([x[0] for x in ratingRelevantCandidates])

    finalRatings = [x for x in ratingRelevantCandidates if (float(x[0]) < ratingMean + 1.5 * ratingSD)]
    finalRatings = [x for x in finalRatings if (float(x[0]) > ratingMean - .75 * ratingSD)]

    finalRatingCandidatesWithWeight = []

    for candidate in finalRatings:
        directorPoints = compareDirectorPoints(toPredict['director'], candidate[1][1]['director'])
        actorPoints = compareActorPoints(toPredict['cast'], candidate[1][1]['cast'])
        voteCountPoints = int(candidate[1][1]['vote_count'])
        matchPoints = candidate[1][0] / np.max([float(x[1][0]) for x in finalRatings]) * 100
        candidateWeight = PREDICTION_MATCHPOINTS_WEIGHT * matchPoints \
                          + PREDICTION_ACTOR_WEIGHT * actorPoints \
                          + PREDICTION_DIRECTOR_WEIGHT * directorPoints \
                          + PREDICTION_VOTECOUNT_WEIGHT * voteCountPoints

        finalRatingCandidatesWithWeight.append((candidateWeight, candidate[0]))

    sumRatingCandidateWeights = np.sum([float(x[0]) for x in finalRatingCandidatesWithWeight])
    sumRatingTimesCandidateWeight = np.sum([float(x[0]) * float(x[1]) for x in finalRatingCandidatesWithWeight])

    ratingPrediction = float(sumRatingTimesCandidateWeight / sumRatingCandidateWeights)

    return ratingPrediction

def calculateDistance(toPredict, toCompare):

    totalDist = 0

    runtimeDist = matchRuntime(toPredict['runtime'], toCompare['runtime'])
    budgetDist = matchBudget(toPredict['budget'], toCompare['budget_adj'])
    directorDist = matchDirector(toPredict['director'], toCompare['director'])
    genreDist = matchGenres(toPredict['genres'], toCompare['genres'])
    actorDist = matchActors(toPredict['cast'], toCompare['cast'])
    companyDist = matchCompanies(toPredict['production_companies'], toCompare['production_companies'])

    totalDist += runtimeDist * RUNTIME_WEIGHT
    totalDist += budgetDist * BUDGET_WEIGHT
    totalDist += directorDist * DIRECTOR_WEIGHT
    totalDist += genreDist * GENRE_WEIGHT
    totalDist += actorDist * ACTOR_WEIGHT
    totalDist += companyDist * COMPANIES_WEIGHT

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

    toCompareLikeCompanies = []

    for company in toCompareCompanies:
        toCompareLikeCompanies = toCompareLikeCompanies + list(set(str(company).split(" ")) - set(toCompareLikeCompanies))

    commonCount = 0.0

    for company in toPredictCompanies:
        companyIndex = toPredictCompanies.index(company)

        if predictCompaniesCloseMatchBooleanList[companyIndex]:
            companyWordsSplit = str(company).split(" ")
            companyWordsSplitIndex = len(companyWordsSplit)

            for index in range(1,companyWordsSplitIndex):
                likeCompany = " ".join(companyWordsSplit[:-index])

                if  likeCompany in toCompareLikeCompanies:
                    commonCount += (companyWordsSplitIndex-index) / float(companyWordsSplitIndex)
        else:
            if company in toCompareCompanies:
                commonCount += 1

    if commonCount >= 3:
        distance = COMPANIES_DIST.get("1")
    elif commonCount == 2:
        distance = COMPANIES_DIST.get("2")
    elif commonCount == 1:
        distance = COMPANIES_DIST.get("3")
    else:
        distance = COMPANIES_DIST.get("4")

    return distance

def checkIfCompaniesCloseMatchesNeeded(dfToPredict,dataSetDf):
    predictCompaniesCloseMatchBooleanList.clear()
    toPredictCompanies = str(dfToPredict['production_companies']).split("|")

    for company in toPredictCompanies:
        companyMatches = dataSetDf[dataSetDf['production_companies'].str.contains(company,na=False)]

        if companyMatches.empty:
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
        distance = DIRECTOR_POINTS_DIST.get("1")
    elif 20000 < points <= 50000:
        distance = DIRECTOR_POINTS_DIST.get("2")
    elif 10000 < points <= 20000:
        distance = DIRECTOR_POINTS_DIST.get("3")
    elif 5000 < points <= 10000:
        distance = DIRECTOR_POINTS_DIST.get("4")
    elif 2000 < points <= 5000:
        distance = DIRECTOR_POINTS_DIST.get("5")
    elif 1000 < points <= 2000:
        distance = DIRECTOR_POINTS_DIST.get("6")
    elif 0 < points <= 1000:
        distance = DIRECTOR_POINTS_DIST.get("7")
    elif points == 0:
        distance = DIRECTOR_POINTS_DIST.get("8")
    else:
        distance = DIRECTOR_POINTS_DIST.get("9")

    return distance

def compareActorPoints(toPredictActors, toCompareActors):

    pointsList = []

    for thePredictActor in str(toPredictActors).split("|"):
        for theCompareActor in str(toCompareActors).split("|"):
            if thePredictActor in theCompareActor:
                if "points" in theCompareActor:
                    pointsIndexStart = theCompareActor.find(":")
                    pointsIndexEnd = theCompareActor.find("points")
                    points = int(theCompareActor[pointsIndexStart + 1:pointsIndexEnd - 1])
                    pointsList.append(points) #match with points
                else:
                    pointsList.append(0) #match without points

    distance = 0

    if len(pointsList) == 0:
        distance = ACTOR_POINTS_DIST.get("8") #do not match

    for finalPoints in pointsList:
        if finalPoints > 90000:
            distance += ACTOR_POINTS_DIST.get("1")
        elif 50000 < finalPoints <= 90000:
            distance += ACTOR_POINTS_DIST.get("2")
        elif 20000 < finalPoints <= 50000:
            distance += ACTOR_POINTS_DIST.get("3")
        elif 10000 < finalPoints <= 20000:
            distance += ACTOR_POINTS_DIST.get("4")
        elif 5000 < finalPoints <= 10000:
            distance += ACTOR_POINTS_DIST.get("5")
        elif 0 < finalPoints <= 5000:
            distance += ACTOR_POINTS_DIST.get("6")
        elif finalPoints == 0:
            distance += ACTOR_POINTS_DIST.get("7")

    return distance

runAlgorithm()

# Test compareGenres()
# toPredict = "Science Fiction|Fantasy|Action|Adventure|Drama|Horror"
# toCompare = "Action|Adventure|Fantasy|Science Fiction"
# result = compareGenres(toPredict, toCompare)
# print("**** " + str(result))

# Predicted Revenue: 205328146.68656018
# 2598
# Predicted Rating: 6.181582164882405

# Predicted Revenue: 246630469.70744947
# 2598
# Predicted Rating: 6.181582164882405