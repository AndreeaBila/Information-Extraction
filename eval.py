from os import listdir
from os.path import isfile, join
import re


if __name__ == "__main__":
    tags = ['paragraph', 'sentence', 'stime', 'etime', 'speaker', 'location']
    files = [f for f in listdir("output/") if isfile(join("output/", f))]

    tagErrors = {}
    for tag in tags:
        tagErrors[tag] = {}
        tagErrors[tag]['TP'] = 0
        tagErrors[tag]['TN'] = 0
        tagErrors[tag]['FP'] = 0
        tagErrors[tag]['FN'] = 0

    totalTP = 0
    totalTN = 0
    totalFP = 0
    totalFN = 0

    for file in files:
        corpus = open("output/" + file, 'r').read()
        classified = open("test_tagged/" + file, 'r').read()

        for tag in tags:
            tagFormat = re.compile("<" + tag + ">" + "(.*?)" + "</" + tag + ">")
            temp = re.compile("<.*?>")
            corpusOccurrences = []
            for occurrence in re.findall(tagFormat, corpus):
                # remove tags
                temp2 = re.sub(temp, "", occurrence)
                corpusOccurrences.append(temp2)

            classifiedOccurrences = []
            for occurrence in re.findall(tagFormat, classified):
                # remove tags
                temp2 = re.sub(temp, "", occurrence)
                classifiedOccurrences.append(temp2)

            TP = 0
            TN = 0
            FP = 0
            FN = 0

            correct = []

            for sth in corpusOccurrences:
                if sth in classifiedOccurrences:
                    TP += 1
                    correct.append(sth)

            for sth in correct:
                if sth in corpusOccurrences:
                    corpusOccurrences.pop(corpusOccurrences.index(sth))
                if sth in classifiedOccurrences:
                    classifiedOccurrences.pop(classifiedOccurrences.index(sth))

            FN = len(corpusOccurrences)
            FP = len(classifiedOccurrences)

            totalTP += TP
            totalTN += TN
            totalFP += FP
            totalFN += FN

            tagErrors[tag]['TP'] += TP
            tagErrors[tag]['TN'] += TN
            tagErrors[tag]['FP'] += FP
            tagErrors[tag]['FN'] += FN


    print("TAG\EVALUATION ", " ACCURACY", "| ", "PRECISION", "  |  ", "RECALL", "  | ", "F1 MEASURE")
    print("--------------------------------------------------------------------")

    for tag in tags:

        accuracy = 0

        if (tagErrors[tag]['TP'] + totalTN + totalFP + totalFN) == 0:
            accuracy = 100
        else:
            accuracy = (tagErrors[tag]['TP'] + totalTN) / (tagErrors[tag]['TP'] + tagErrors[tag]['TN'] + tagErrors[tag]['FP'] + tagErrors[tag]['FN']) * 100

        precision = 0

        if (tagErrors[tag]['TP'] + totalFP) == 0:
            precision = 100
        else:
            precision = tagErrors[tag]['TP'] / (tagErrors[tag]['TP'] + tagErrors[tag]['FP']) * 100

        recall = 0

        if (tagErrors[tag]['TP'] + totalFN) == 0:
            recall = 100
        else:
            recall = tagErrors[tag]['TP'] / (tagErrors[tag]['TP'] + tagErrors[tag]['FN']) * 100

        f1 = 0
        if (precision + recall) == 0:
            f1 = 100
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        print(tag + (17-len(tag)) * " ", str(round(accuracy, 2)) + "%", "     ", str(round(precision, 2)) + "%", "      ", str(round(recall, 2)) + "%", "      ", str(round(f1, 2)) + "%")


    accuracy = 0

    if (totalTP + totalTN + totalFP + totalFN) == 0:
        accuracy = 100
    else:
        accuracy = (totalTP + totalTN) / (totalTP + totalTN + totalFP + totalFN) * 100

    precision = 0

    if (totalTP + totalFP) == 0:
        precision = 100
    else:
        precision = totalTP / (totalTP + totalFP) * 100

    recall = 0

    if (totalTP + totalFN) == 0:
        recall = 100
    else:
        recall = totalTP / (totalTP + totalFN) * 100

    f1 = 0
    if (precision + recall) == 0:
        f1 = 100
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    print("TOTAL" + 12 * " " , str(round(accuracy, 2)) + "%", "     ", str(round(precision, 2)) + "%", "      ", str(round(recall, 2)) + "%", "      ", str(round(f1, 2)) + "%")





