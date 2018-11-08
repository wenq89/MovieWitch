import pandas as pd

# Distribution of points for the runtime comparison
RUNTIME_DIST = {"1": 100, "2": 92.1, "3": 82.7, "4": 71.2, "5": 56.5, "6": 35.6, "7": 0}

# Distribution of points for the budget comparison
BUDGET_DIST = {"1": 100, "2": 89.8, "3": 77.4, "4": 61.3, "5": 38.7, "6": 0}

BUDGET_WEIGHT = 1000
RUNTIME_WEIGHT = 1000

NUM_CANDIDATES = 20 #The number of candidates to keep track of

def runAlgorithm():

    dataSetDF = pd.read_csv('tmbdWithPoints.csv', dtype='object')
    dfToPredict = pd.read_csv('toPredict.csv', dtype='object').iloc[0]

    topCandidates = []


    for i in range(NUM_CANDIDATES):
        topCandidates.append((0, None))

    print(len(topCandidates))

    for index, row in dataSetDF.iterrows(): #Iterate all rows in our data-set

        currentDist = calculateDistance(dfToPredict, row)

        if currentDist > topCandidates[NUM_CANDIDATES - 1][0]:
            topCandidates[NUM_CANDIDATES - 1] = (currentDist, row)
            topCandidates = sorted(topCandidates, key=lambda x: x[0], reverse=True)

    for i in range(NUM_CANDIDATES):
        print("\nCandidate " + str(i + 1) + " Points: " + str(topCandidates[i][0]) + "   \n" + str(topCandidates[i][1]))

    #Make the prediction based on the top candidates found
    makePrediction(topCandidates)

def makePrediction(candidateList):
    None

def calculateDistance(toPredict, toCompare):

    totalDist = 0

    runtimeDist = compareRuntime(toPredict['runtime'], toCompare['runtime'])
    budgetDist = compareBudget(toPredict['budget'], toCompare['budget'])

    totalDist += runtimeDist * RUNTIME_WEIGHT
    totalDist += budgetDist  * BUDGET_WEIGHT

    return totalDist

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


runAlgorithm()