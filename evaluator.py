import re
from os import listdir
from os.path import isfile, join

files = []
tags =  []


def getFiles():
    myPath = "output/"
    files = [f for f in listdir(myPath) if isfile(join(myPath, f))]
    return files


def removeTags(text):
    tag = re.compile("<.*?")
    return re.sub(tag, '', text)


def findContent(content, tag):
    tagFormat = re.compile( "<" + tag + ">" + "(.*?)" + "</" + tag + ">")

    occurrences = []

    for occurrence in re.findall(tagFormat, content):
        occurrences.append(removeTags(occurrence))

    return occurrences


def getErrors(corpus, classified):
    truePositives = 0
    trueNegatives = 0

    toPop = []

    for tag in corpus:
        if tag in classified:
            truePositives += 1
            toPop.append(tag)

    for tag in toPop:
        if tag in corpus:
            corpus.pop(corpus.index(tag))
        if tag in classified:
            classified.pop(classified.index(tag))

    falseNegatives = len(corpus)
    falsePositives = len(classified)

    return (truePositives, trueNegatives, falsePositives, falseNegatives)


def computeAccuracy(truePositives, trueNegatives, falsePositives, falseNegatives):
    if (truePositives + trueNegatives + falsePositives + falseNegatives) == 0:
        return 100
    else:
        return (truePositives + trueNegatives) / (truePositives + trueNegatives + falsePositives + falseNegatives) * 100


def computePrecision(truePositivesClassified, falsePositivesClassified):
    allClassified = truePositivesClassified + falsePositivesClassified
    if allClassified == 0:
        return 100
    return truePositivesClassified / allClassified * 100


def computeRecall(truePositivesClassified, falseNegativesCorpus):
    all = truePositivesClassified + falseNegativesCorpus
    if all == 0:
        return 100
    return truePositivesClassified / all * 100


def computeFMeasure(precision, recall):
    if (precision + recall) == 0:
        return 100
    return 2 * ((precision * recall) / (precision + recall))


def evaluate():
    tags = ['paragraph', 'sentence', 'stime', 'etime', 'speaker', 'location']
    files = getFiles()

    mapTagEval = {}
    for tag in tags:
        mapTagEval[tag] = {}
        mapTagEval[tag]['truePositives'] = 0
        mapTagEval[tag]['trueNegatives'] = 0
        mapTagEval[tag]['falsePositives'] = 0
        mapTagEval[tag]['falseNegatives'] = 0

    totalTruePositives = 0
    totalTrueNegatives = 0
    totalFalsePositives = 0
    totalFalseNegatives = 0

    for file in files:
        corpusPath = "output/" + file
        classifiedPath = "test_tagged/" + file

        corpusContent = open(corpusPath, 'r').read()
        classifiedContent = open(classifiedPath, 'r').read()

        for tag in tags:

            corpusTag = findContent(corpusContent, tag)
            classifiedTag = findContent(classifiedContent, tag)

            truePostives, trueNegatives, falsePositives, falseNegatives = getErrors(corpusTag, classifiedTag)
            totalTruePositives = totalTruePositives + truePostives
            totalTrueNegatives = totalTrueNegatives + trueNegatives
            totalFalsePositives = totalFalsePositives + falsePositives
            totalFalseNegatives = totalFalseNegatives + falseNegatives

            mapTagEval[tag]['truePositives'] = mapTagEval[tag]['truePositives'] + truePostives
            mapTagEval[tag]['trueNegatives'] = mapTagEval[tag]['trueNegatives'] + trueNegatives
            mapTagEval[tag]['falsePositives'] = mapTagEval[tag]['falsePositives'] + falsePositives
            mapTagEval[tag]['falseNegatives'] = mapTagEval[tag]['falseNegatives'] + falseNegatives

    accuracy = computeAccuracy(totalTruePositives, totalTrueNegatives, totalFalsePositives, totalFalseNegatives)
    precision = computePrecision(totalTruePositives, totalFalsePositives)
    recall = computeRecall(totalTruePositives, totalFalseNegatives)
    f1Measure = computeFMeasure(precision, recall)

    print("TAG                   Accuracy    Precision   Recall      F1 measure")
    print("total" + (10 - len("total")) * ' ' + "             {a:.2f}%      {p:.2f}%      {r:.2f}%      {f:.2f}%".format(a=accuracy, p=precision, r=recall, f=f1Measure))

    for tag in tags:
        accuracy = computeAccuracy(mapTagEval[tag]['truePositives'], mapTagEval[tag]['trueNegatives'], mapTagEval[tag]['falsePositives'], mapTagEval[tag]['falseNegatives'])
        precision = computePrecision(mapTagEval[tag]['truePositives'], mapTagEval[tag]['falsePositives'])
        recall = computeRecall(mapTagEval[tag]['truePositives'], mapTagEval[tag]['falseNegatives'])
        f1Measure = computeFMeasure(precision, recall)

        print(tag + (10 - len(tag)) * ' ' + "             {a:.2f}%      {p:.2f}%      {r:.2f}%      {f:.2f}%".format(a=accuracy, p=precision, r=recall, f=f1Measure))

    return


if __name__ == "__main__":
    evaluate()