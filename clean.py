from os import listdir
from os.path import isfile, join
from utilities import emptyOutputFolder
from wikification import wikification
import nltk
import re

mapFiles        = {}
mapHeaders      = {}
mapContent      = {}
mapTags         = {}
speakers        = set()
locations       = set()
topics          = []
types           = []
classification  = {}
tree            = {}

def readContents():
    myPath = "untagged/"
    onlyfiles = [f for f in listdir(myPath) if isfile(join(myPath, f))]

    # read each file
    for fileName in onlyfiles:
        # construct file name and read the file
        filePath = myPath + fileName
        file = open(filePath, "r")
        fileContent = file.read()

        # map file content by file name
        mapFiles[fileName] = fileContent

        # headers
        temporary = fileContent.split("Abstract:")
        mapHeaders[fileName] = temporary[0];
        if "Abstract" in fileContent:
            mapContent[fileName] = temporary[1]
        else:
            mapContent[fileName] = ""

        speaker = findHeaderSpeaker(fileName)
        if speaker is not None:
            speakers.add(speaker)

        location = findHeaderLocation(fileName)
        if location is not None:
            locations.add(re.escape(location))

        tree = buildTree()



def extractTrainingData():
    myPath = "training/"
    onlyfiles = [f for f in listdir(myPath) if isfile(join(myPath, f))]

    # Read each file
    for fileName in onlyfiles:

        filePath = myPath + fileName
        fileContent = open(filePath, "r").read()
        file = '\n'.join(fileContent.split('\n')[1:])


        rex = re.compile(r'<.*?>(.*?)</.*?>', re.S | re.M)

        tags = rex.finditer(file)

        if tags:
            label = re.compile("<.*?>")
            for x in tags:
                text = x.group(1).strip()
                text = text.replace("\n", " ")
                temp = label.match(x.group())
                tag = temp.group(0)[1:-1]

                if tag == 'speaker':
                    speakers.add(text)
                elif tag == 'location':
                        locations.add(text)



def tag(index, text, fileName, tagName):

    content = mapFiles[fileName]
    content = content[:(index + len(text))] + "</" + tagName + ">" + content[(index + len(text)):]
    content = content[:index] + "<" + tagName + ">" + content[index:]
    mapFiles[fileName] = content


def hasVerb(text):
    words = nltk.word_tokenize(text)

    for word, part in nltk.pos_tag(words):
        if 'V' in part:
            return True
            break

    return False


def isSentence(text):
    if text.strip() != "":
        if text.strip()[0] == '-' or text.strip()[0] == "*" or text.strip()[0] == "~":
            return False
    keywords = ['type:', 'who:', 'dates:', 'time:', 'place:', 'duration:', 'host:', 'when:', 'where:', 'speaker:', 'title:', 'futherdetails', '---']
    for word in keywords:
        if word in text.lower():
            return False
    if hasVerb(text):
        return True


def tagSentences(paragraph,fileName):
    sentences = nltk.sent_tokenize(paragraph)

    for sentence in sentences:
        if hasVerb(sentence):
            sentence = sentence.strip()
            position = mapFiles[fileName].find(sentence)
            tag(position, sentence[:-1], fileName, "sentence")

    return


def tagParagraphs(fileName):
    paragraphs = mapContent[fileName].split("\n\n")

    for paragraph in paragraphs:
        if isSentence(paragraph):
            paragraph = paragraph
            position = mapFiles[fileName].find(paragraph)
            tag(position, paragraph, fileName, "paragraph")
            tagSentences(paragraph, fileName)

    return


def findHeaderLocation(fileName):
    headerHint = "Place:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    if temp is None:
        return

    line = temp.group(1).strip()

    return line


def tagLocation(fileName):
    tagLength = len("<location></location>")

    for location in locations:
        counter = 0
        for loc in re.finditer(location, mapFiles[fileName]):
            index = loc.start() + counter * tagLength
            loc = loc.group().strip()
            tag(index, loc, fileName, 'location')
            counter = counter + 1

    return


def findHeaderSpeaker(fileName):
    headerHint = "Who:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    if temp is None:
        return

    line = temp.group(1).strip()
    temp2 = re.split(',|/|-|\(', line)
    name = temp2[0]

    return name


def tagSpeaker(fileName):
    tagLength = len("<speaker></speaker>")

    for speaker in speakers:
        counter = 0

        for s in re.finditer(speaker, mapFiles[fileName]):

            index = s.start() + counter * tagLength
            s = s.group().strip()
            tag(index, s, fileName, 'speaker')
            counter = counter + 1

    return


def tagTime(fileName):
    headerHint = "Time:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    if temp is None:
        return

    headerTimes = temp.group(1).split("-")

    if len(headerTimes) == 1:
        mapTags[fileName]['stime'] = headerTimes[0].strip()
        mapTags[fileName]['etime'] = "EMPTY"
    elif len(headerTimes) == 2:
        mapTags[fileName]['stime'] = headerTimes[0].strip()
        mapTags[fileName]['etime'] = headerTimes[1].strip()
    else:
        mapTags[fileName]['stime'] = "EMPTY"
        mapTags[fileName]['etime'] = "EMPTY"

    time_format = re.compile(r"\b((0?[1-9]|1[012])([:.][0-5][0-9])?(\s?[apAP][Mm])|([01]?[0-9]|2[0-3])([:.][0-5][0-9]))\b")

    counter = 0
    tagLength = len("<stime></stime>")

    contentTimes = time_format.finditer(mapFiles[fileName])

    for time in contentTimes:
        index = time.start() + counter * tagLength
        word = time.group().strip()
        if word.lower() == mapTags[fileName]['stime'].lower():
            tag(index, word, fileName, 'stime')
            counter = counter + 1
        elif word.lower() == mapTags[fileName]['etime'].lower():
            tag(index, word, fileName, 'etime')
            counter = counter + 1

    return


def printTaggedFiles():
    # Empty the output folder
    emptyOutputFolder("output/")

    for file in mapFiles:
        outputFilePath =  "output/" + file
        out = open(outputFilePath, 'w')
        print(mapFiles[file], end="", file=out)

    return


def buildTree():
    subjects = ["Science", "Humanities"]

    for subject in subjects:
        tree[subject] = {}

    tree['Science'] = {"Computer Science": {}, "Physics": {}, "Chemistry": {}}
    tree['Humanities'] = {"Literature": {}, "History": {}, "Music": {}}

    tree['Science']['Computer Science'] = {"artificial intelligence": {'deep learning', 'machine learning',
                                            'neural network', 'neural net', 'minimax', 'alpha-beta pruning', 'ai '},
                                           "human computer interaction": {'hci'}, "security": {},
                                           "robotics": {'robot', 'robotics', 'robotic'}, 'computer vision':
                                            {'vision', 'data visualization', 'image conversion'}, 'computer graphics':
                                            {'graph', 'graphics'}, 'networks': {}, 'databases': {'sql', 'database'},
                                           'parallel computing': {}, 'algorithms': {}, 'programming languages': {},
                                           'automata': {'finite state machines'}, 'technology': {}}

    tree['Science']['Physics'] = {"thermodynamics": {}, "quantum mechanics": {}, "optical physics": {}}

    tree['Science']['Chemistry'] = {"organic Chemistry": {}, "inorganic chemistry": {}, "biochemistry": {'biomolecule'}}

    tree['Science']['Engineering'] = {"mechanical engineering": {}, "electrical engineering": {},
                                      "industrial engineering": {}, "environmental engineering": {}, 'transport': {}}

    tree['Science']['Mathematics'] = {"algebra": {}, "geometry": {'geometric'}, "calculus": {}, "combinatorics": {},
                                      'math': {}, 'arithmetic': {}, 'mathematical theory': {}}

    tree['Science']['Economy'] = {"taxes": {'tax'}, 'finance': {'financial'}}

    tree['Humanities']['Public speaking'] = {"speech": {}}

    tree['Humanities']['Teaching'] = {"teaching": {}}

    return tree


def getTopic(fileName):
    headerHint = "Topic:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    if temp is None:
        return

    headerTopic = temp.group(1).strip()
    mapTags[fileName]['topic'] = headerTopic
    topics.append(headerTopic)
    return


def getType(fileName):

    headerHint = "Type:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    if temp is None:
        return

    headerType = temp.group(1).strip()
    mapTags[fileName]['type'] = headerType
    types.append(headerType)
    return


def ontology(fileName):

    if fileName not in classification:
        if 'topic' in mapTags[fileName]:
            topic = mapTags[fileName]['topic'].rstrip()
            titles = wikification(topic)
            for subjectType in tree:
                for domain in tree[subjectType]:
                    for field in tree[subjectType][domain]:
                        if topic is not None:
                            try:
                                if titles is not None:
                                    for title in titles:
                                        if field in title.lower():
                                            classification[fileName] = field + ", " + domain + ", " + subjectType
                                            return
                                        elif domain in title:
                                            classification[fileName] = domain + ", " + subjectType
                                            return
                            except Exception as e:
                                print("Timed out")


                        for keyword in tree[subjectType][domain][field]:
                            if topic is not None:
                                try:
                                    if titles is not None:
                                        for title in titles:
                                            if keyword in title.lower():
                                                classification[fileName] = field + ", " + domain + ", " + subjectType
                                                return
                                except Exception as e:
                                    print("Timed out")

    if fileName not in classification:
        if 'topic' in mapTags[fileName]:
            topic = mapTags[fileName]['topic'].rstrip()
            for subjectType in tree:
                for domain in tree[subjectType]:
                    for field in tree[subjectType][domain]:
                        if topic is not None:
                            if field in topic.lower():
                                classification[fileName] = field + ", " + domain + ", " + subjectType
                                return
                            elif domain in topic:
                                classification[fileName] = domain + ", " + subjectType
                                return
                        for keyword in tree[subjectType][domain][field]:
                            if topic is not None:
                                if keyword in topic.lower():
                                    classification[fileName] = field + ", " + domain + ", " + subjectType
                                    return

    if fileName not in classification:
        content = mapContent[fileName].rstrip()
        for subjectType in tree:
            for domain in tree[subjectType]:
                for field in tree[subjectType][domain]:
                    if content is not None:
                        if field in content.lower():
                            classification[fileName] = field + ", " + domain + ", " + subjectType
                            return
                        elif domain in content:
                            classification[fileName] = domain + ", " + subjectType
                            return
                    for keyword in tree[subjectType][domain][field]:
                        if content is not None:
                            if keyword in content.lower():
                                classification[fileName] = field + ", " + domain + ", " + subjectType
                                return

    return

def printOntology():
    out = open('ontology-classification.txt', 'w')
    for subjectType in tree:
        print(subjectType.upper() + "\n", end="", file=out)
        for domain in tree[subjectType]:
            print(domain + "\n", end="", file=out)
            for field in tree[subjectType][domain]:
                print(field.title() + "\n", end="", file=out)
                print("-" * len(field), "\n", end="", file=out)
                for obj in classification:
                    if field in classification[obj]:
                        if 'topic' in mapTags[obj]:
                            print(obj, ':', mapTags[obj]['topic'], "\n", end="", file=out)
                print("\n", end="", file=out)
            print('\n', end="", file=out)


if __name__ == '__main__':

    # read the file contents from the folder
    print('Tagging files...')
    emptyOutputFolder("output/")
    readContents()

    for fileName in mapFiles:
        mapTags[fileName] = {}

        tagParagraphs(fileName)
        tagLocation(fileName)
        tagSpeaker(fileName)
        tagTime(fileName)
        getTopic(fileName)
        getType(fileName)

    printTaggedFiles()
    print('Finished tagging files')
    print('Classifying emails...')
    for fileName in mapFiles:
        ontology(fileName)
        printOntology()
    print('Finished classifying emails')
    print('Check ontology-classification.txt to see the classified emails')
