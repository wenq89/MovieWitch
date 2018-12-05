import pandas as pd
import numpy as np

"""
    Final Project COMP 4710 Fall 2018
    Authors: Amanjyot Singh Sainbhi, Kevin Tran, Lucas Eckhardt, Qi Wen
    Description: This program must be located in the same folder as the files tmdbWithPointsV2.csv and toPredict.csv
                This implementation of our algorithm will predict the rating and revenue for all test movies in the 
                toPredict.csv file and will be able to also predict for any movies added to that file in the same format.
    Date: December 4 2018
"""
# Distribution of points for the intervals we are capturing during the matching stage of the algorithm
RUNTIME_DIST = {"1": 100, "2": 92.1, "3": 82.7, "4": 71.2, "5": 56.5, "6": 35.6, "7": 0}
BUDGET_DIST = {"1": 100, "2": 89.8, "3": 77.4, "4": 61.3, "5": 38.7, "6": 0}
DIRECTOR_DIST = {"1": 100, "2": 0}
ACTOR_DIST = {"1": 100, "2": 89.8, "3": 77.4, "4": 61.3, "5": 38.7, "6": 0}
COMPANIES_DIST = {"1": 100, "2": 79.2, "3": 50, "4": 0}

#Point distributions used in the prediction stage
DIRECTOR_POINTS_DIST = {"1": 100, "2": 85, "3": 70, "4": 50, "5": 30, "6": 15, "7": 10, "8": 5, "9": 0}
ACTOR_POINTS_DIST = {"1": 100, "2": 85, "3": 70, "4": 50, "5": 30, "6": 10, "7": 5, "8": 0}

#Weights used to match closeness of candidates, change based on if predicting rating or revenue as indicated
BUDGET_WEIGHT = 5 #rating:1, revenue:5
RUNTIME_WEIGHT = 1 #rating:1, revenue:1
DIRECTOR_WEIGHT = 20 #rating:5, revenue:20
GENRE_WEIGHT = 0 #rating:2, revenue:0
ACTOR_WEIGHT = 10 #rating:7, revenue:10
COMPANIES_WEIGHT = 30 #rating:1, revenue:30

#Weights used to make the prediciton based off of the candidates, change based on if predicting rating or revenue as indicated
PREDICTION_ACTOR_WEIGHT = 100 #rating:3, revenue:100
PREDICTION_DIRECTOR_WEIGHT = 50 #rating:4, revenue:50
PREDICTION_MATCHPOINTS_WEIGHT = 10 #rating:5, revenue:10
PREDICTION_VOTECOUNT_WEIGHT = 1 #rating:3, revenue:1

# The number of candidates to keep track of, changes based on if predicting rating or revenue as indicated
NUM_CANDIDATES = 4 #rating:13, revenue:4

# if true, gets rating predictions
# if false, gets revenue predictions
PREDICT_RATING = False

#Testing variables to report % difference between prediction and actual value
withinFive = []
withinTen = []
withinFifteen = []
withinTwenty = []
withinThirty = []

#List of boolean, in same order as companies given, to see if close match is required
predictCompaniesCloseMatchBooleanList = []

def runAlgorithm():
    """Main method of the program, reads in the list of test cases and the dataset into pandas dataframes. Compares all
        movies in the dataset to each candidate in the test cases and then calls makePrediction to predict for the current
        test movie."""

    #Reading in the dataset
    dataSetDF = pd.read_csv('tmbdWithPointsV2.csv', dtype='object')

    #Reading in the test cases
    dataFrame = pd.read_csv('toPredict.csv', dtype='object', error_bad_lines=False)

    for dfToPredict in dataFrame.iterrows(): #Loop through each movie to predict for in the test cases

        print("*******************************************************************************************************")
        dfToPredict = dfToPredict[1]
        checkIfCompaniesCloseMatchesNeeded(dfToPredict, dataSetDF)

        topCandidates = []

        #Initialize a candidate list to keep track of the best candidates
        for i in range(NUM_CANDIDATES):
            topCandidates.append((0, None))

        for index, row in dataSetDF.iterrows():  # Iterate all rows in our data-set

            #Calculate the current matching score between the test movie and the current dataset movie
            currentDist = calculateDistance(dfToPredict, row)

            #If the matching score is higher than the lowest one in our candidate list swap them out and reorder the candidates
            if currentDist > topCandidates[NUM_CANDIDATES - 1][0]:
                topCandidates[NUM_CANDIDATES - 1] = (currentDist, row)
                topCandidates = sorted(topCandidates, key=lambda x: x[0], reverse=True)

        # Make the prediction based on the top candidates found
        makePrediction(dfToPredict,topCandidates)

    #Print test results
    print()
    print("Within 5%: " + str(len(withinFive)))
    print("Within 10%: " + str(len(withinTen)))
    print("Within 15%: " + str(len(withinFifteen)))
    print("Within 20%: " + str(len(withinTwenty)))
    print("Within 30%: " + str(len(withinThirty)))

def makePrediction(toPredict,candidateList):
    """Makes calls to both predictRating and predictRevenue and prints out the predicitons along with the actual values"""

    print("Predicting for: " + toPredict['title'])

    if PREDICT_RATING:
        actualRating = float(toPredict['actual_imdb_rating'])
        predictedRating = predictRating(toPredict, candidateList)
        percentDiff = round((actualRating - predictedRating) / actualRating * 100, 2)
        print("Predicted rating: " + str(predictedRating) + " Actual Rating: " + str(actualRating))
        print("Difference in rating prediction: " + str(percentDiff) + "%")
    else:
        actualRevenue = int(toPredict['actual_revenue'])
        predictedRevenue = predictRevenue(toPredict,candidateList)
        percentDiff = round((actualRevenue - predictedRevenue) / actualRevenue * 100, 2)
        print(str("Predicted revenue: " + str(predictedRevenue) + " Actual Revenue: " + str(actualRevenue)))
        print("Difference in revenue prediction: " + str(percentDiff) + "%")

    #Tabulate how close the prediction was based on percent difference
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

def predictRevenue(toPredict, candidateList):
    """Makes the revenue prediction. Removes outliers. Reweights the candidates based on actor and director popularity
    and the matching score from stage 1. Then takes a weighted average to predict the revenue and returns it"""

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


    #Calculate the weights for each of the remaining candidates
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
    """Makes the rating prediction. Removes outliers. Reweights the candidates based on actor and director popularity the
    matching score from stage 1 and the number of votes received. Then takes a weighted average to predict the rating and returns it"""

    ratingRelevantCandidates = []

    #Remove candidates with no rating specified
    for candidate in candidateList:

        currentCandidate = candidate[1]

        if float(currentCandidate['vote_avg']) > 0:
            ratingRelevantCandidates.append((float(currentCandidate['vote_avg']), candidate))

    #Remove outlier candidates based on rating
    ratingMean = np.mean([x[0] for x in ratingRelevantCandidates])
    ratingSD = np.std([x[0] for x in ratingRelevantCandidates])

    finalRatings = [x for x in ratingRelevantCandidates if (float(x[0]) < ratingMean + 1.5 * ratingSD)]
    finalRatings = [x for x in finalRatings if (float(x[0]) > ratingMean - .75 * ratingSD)]

    finalRatingCandidatesWithWeight = []

    #Weight each candidate based on vote count, direct and actor popularity and matching score from part 1
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

    #Calculate the prediction
    sumRatingCandidateWeights = np.sum([float(x[0]) for x in finalRatingCandidatesWithWeight])
    sumRatingTimesCandidateWeight = np.sum([float(x[0]) * float(x[1]) for x in finalRatingCandidatesWithWeight])

    ratingPrediction = float(sumRatingTimesCandidateWeight / sumRatingCandidateWeights)

    return ratingPrediction

def calculateDistance(toPredict, toCompare):
    """Calculates the total matching score for the candidate. Score is based on runtime, budget, director, actors, companies
    and genres. Sums up the matching score of each catergoy * the categories weight and returns the matching score."""
    totalDist = 0

    #Calculate the matching score for each attribute
    runtimeDist = matchRuntime(toPredict['runtime'], toCompare['runtime'])
    budgetDist = matchBudget(toPredict['budget'], toCompare['budget_adj'])
    directorDist = matchDirector(toPredict['director'], toCompare['director'])
    genreDist = matchGenres(toPredict['genres'], toCompare['genres'])
    actorDist = matchActors(toPredict['cast'], toCompare['cast'])
    companyDist = matchCompanies(toPredict['production_companies'], toCompare['production_companies'])

    #Sum up the individual atrribute matching scores time their weights
    totalDist += runtimeDist * RUNTIME_WEIGHT
    totalDist += budgetDist * BUDGET_WEIGHT
    totalDist += directorDist * DIRECTOR_WEIGHT
    totalDist += genreDist * GENRE_WEIGHT
    totalDist += actorDist * ACTOR_WEIGHT
    totalDist += companyDist * COMPANIES_WEIGHT

    return totalDist


def evaluateVoteCount(toCompare):
    """Evaluates how relevant the vote count should be in the rating prediction depending on how many votes the candidate
    has received to determine its rating. Returns a point value between 0-100, 0 being no relevance."""

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
    """Returns a matching score from 0-100 based on the proportion of genres in toPredicts genre list that are also in
    toCompares genre set. 100 is returned if all genres in toPredicts set are also in toCompares set."""

    #Get the sets of genres
    toPredictGenres = str(toPredictGenresString).split("|")
    toCompareGenres = str(toCompareGenresString).split("|")

    toCompareGenresSet = set(toCompareGenres)

    commonCount = 0

    #Count how many are common to the two sets
    for genre in toPredictGenres:
        if genre in toCompareGenresSet:
            commonCount += 1

    #Return 100 times the proportion in both
    return 100 * commonCount/len(toPredictGenres)


def matchRuntime(toPredictRuntime, toCompareRuntime):
    """Returns a matching score from 0-100 based on the similarity of the runtimes. The absolute value of the differnece in
    minutes between the movies runtimes is calculated and then looked up to find the point interval that should be returned."""

    #Calculate the difference in runtimes
    diff = abs(int(toPredictRuntime) - int(toCompareRuntime))

    #Lookup the point interval that should be returned for the difference in runtime

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
    """Returns a matching score form 0-100 based on the difference in budgets of the movies. The absolute value of the percent
    difference in budgets is calculated and then the point interval is looked up and returned."""

    #Calculate the % difference
    diff = abs(int(toPredictBudget) - int(toCompareBudget)) / int(toPredictBudget) * 100

    #Lookup the interval to return the correct number of points
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
    """Returns a matching score between 0-100 based on purely the similarity between actors in the movies. Calculated by
    taking the number of common actors in the toPredict actors set that are also in the toCompare actors set. Then looking
    up this in the if block to determine how many points should be returned"""

    toPredictActors = str(toPredictActors).split("|")
    toCompareActors = str(toCompareActors).split("|")

    toPredictActorsList = []
    toCompareActorsList = []

    #Remove point values after actors names so that they dont get in the way of name comparison
    for i in toPredictActors:
        toPredictActorsList.append(i.split(":")[0])

    for j in toCompareActors:
        toCompareActorsList.append(j.split(":")[0])

    toCompareActorsSet = set(toCompareActorsList)

    commonCount = 0

    #Calculate the number of common actors
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
    """Returns a matching score between 0-100 based on purely the similarity between production companies of the movies.
    Calculated by taking the number of common production companies in the toPredict production companies set that are
    also in the toCompare production companies set. Then looking up this in the if block to determine how many points
    should be returned. That is when a production company appears somewhere in the database. If it does not appear then
    a set of words are created from the toCompare production companies set. Then depending on amount of similar words
    of the toPredict production company found in the words set, a fraction of commonCount is given which then gets
    transformed to how many points should be returned"""
    toPredictCompanies = str(toPredictCompanies).split("|")
    toCompareCompanies = str(toCompareCompanies).strip("|").split("|")

    # toCompareLikeCompanies = []

    # for company in toCompareCompanies:
    #     toCompareLikeCompanies = toCompareLikeCompanies + list(set(str(company).split(" ")) - set(toCompareLikeCompanies))

    commonCount = 0.0

    for predictCompany in toPredictCompanies:
        predictCompanyIndex = toPredictCompanies.index(predictCompany)

        if predictCompaniesCloseMatchBooleanList[predictCompanyIndex]:
            predictCompanyWordsSplit = str(predictCompany).split(" ")

            for compareCompany in toCompareCompanies:
                numWordsMatched = 0
                matchedPrevWord = True
                for predictcompanyword in predictCompanyWordsSplit:
                    if matchedPrevWord:
                        if predictcompanyword in compareCompany:
                            numWordsMatched += 1
                        else:
                            break

                if numWordsMatched > 0:
                    numCompareCompanyWords = len(str(compareCompany).split(" "))
                    if (numWordsMatched / numCompareCompanyWords) > 0.5:
                        commonCount += 1
                    else:
                        commonCount += 0.5
        else:
            if predictCompany in toCompareCompanies:
                commonCount += 1

    # commonCount = round(commonCount)
    if commonCount >= 3:
        distance = COMPANIES_DIST.get("1")
    elif commonCount >= 2:
        distance = COMPANIES_DIST.get("2")
    elif commonCount >= 1:
        distance = COMPANIES_DIST.get("3")
    else:
        distance = COMPANIES_DIST.get("4")

    return distance

def checkIfCompaniesCloseMatchesNeeded(dfToPredict,dataSetDf):
    """This resets the predictCompaniesCloseMatchBooleanList so that the position matching toPredict companies is true
    if that company name is not found in the database and requires close Matching otherwise it gets set to false"""
    predictCompaniesCloseMatchBooleanList.clear()
    toPredictCompanies = str(dfToPredict['production_companies']).split("|")

    for company in toPredictCompanies:
        companyMatches = dataSetDf[dataSetDf['production_companies'].str.contains(u'\|'+company+'\|',na=False)]

        if companyMatches.empty:
            predictCompaniesCloseMatchBooleanList.append(True)
        else:
            predictCompaniesCloseMatchBooleanList.append(False)


def matchDirector(toPredictDirector, toCompareDirector):
    """Returns a matching score either a 0 or 100. 100 if the movies have the same director and 0 if they do not"""
    if str(toPredictDirector) in str(toCompareDirector):
        distance = DIRECTOR_DIST.get("1")
    else:
        distance = DIRECTOR_DIST.get("2")

    return distance


def compareDirectorPoints(toPredictDirector, toCompareDirector):
    """Returns a value 0-100 to be used in the prediction phase of the algorithm. The value is determined based on the
    popularity of the director if it's similar between the 2 movies. Higher point value means a more popular director. If
    the director is a top 10 director in our ranking list then 100 points will be returned all the way down to 0 points if the
    directors don't match even."""

    points = -1

    #Find if the directors match and if so how popular the matching director is
    if str(toPredictDirector) in str(toCompareDirector):
        for multiDirectors in str(toCompareDirector).split("|"):
             if str(toPredictDirector) in multiDirectors:
                 if "points" in multiDirectors:
                     pointsIndexStart = multiDirectors.find(":")
                     pointsIndexEnd = multiDirectors.find("points")
                     points = int(multiDirectors[pointsIndexStart + 1:pointsIndexEnd - 1])
                 else:
                     points = 0

    #Get a point value to return based on the popularity score of the director.
    #Any director between 50000-20000 points was in the top 10 of the directors ranking list we used
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
    elif points == 0: #Return a base amount of points if the director matches but we have no ranking for them in our list
        distance = DIRECTOR_POINTS_DIST.get("8")
    else: #Return no points if the director doesnt matching between toPredict and this candidate
        distance = DIRECTOR_POINTS_DIST.get("9")

    return distance

def compareActorPoints(toPredictActors, toCompareActors):
    """Returns a point value to be used in the prediction phase of the algorithm. The value is determined based on the
        popularity of the actors that are similar between the movies. Higher point value means a more popular actor. There could
        be multilple similar actors with point rankings which will be taken into consideration."""

    pointsList = []

    #Find similar actors between toPredict and the candidate toCompare
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

    #If there are no matching actors between toPredict and this candidate return 0 points
    if len(pointsList) == 0:
        distance = ACTOR_POINTS_DIST.get("8") #do not match

    #Sum up the point values based on how popular the matching actors are
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