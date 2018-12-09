from os import listdir
from os.path import isfile, join
from utilities import emptyOutputFolder
import nltk
import re

mapFiles    = {}
mapHeaders  = {}
mapContent  = {}
mapTags     = {}
speakers    = set()
locations   = set()
topics      = []
types       = []

def readContents():
    myPath = "untagged/"
    onlyfiles = [f for f in listdir(myPath) if isfile(join(myPath, f))]

    # Read each file
    for fileName in onlyfiles:
        # Construct file name and read the file
        filePath = myPath + fileName
        file = open(filePath, "r")
        fileContent = file.read()

        # Map file content by file name
        mapFiles[fileName] = fileContent

        # Headers
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


    # extractTrainingData()


def extractTrainingData():
    myPath = "training/"
    onlyfiles = [f for f in listdir(myPath) if isfile(join(myPath, f))]

    # Read each file
    for fileName in onlyfiles:
        # Construct file name and read the file
        filePath = myPath + fileName
        fileContent = open(filePath, "r").read()
        file = '\n'.join(fileContent.split('\n')[1:])


        # file = files["1.txt"]
        rex = re.compile(r'<.*?>(.*?)</.*?>', re.S | re.M)

        tags = rex.finditer(file)

        if tags:
            label = re.compile("<.*?>")
            for x in tags:
                text = x.group(1).strip()
                text = text.replace("\n", " ")
                temp = label.match(x.group())
                tag = temp.group(0)[1:-1]
                # if tag == 'speaker':
                #     speakers.add(text)
                if tag == 'speaker':
                    speakers.add(text)



def tag(index, text, fileName, tagName):
    startTag = "<" + tagName + ">"
    endTag = "</" + tagName + ">"

    content = mapFiles[fileName]
    content = content[:(index + len(text))] + endTag + content[(index + len(text)):]
    content = content[:index] + startTag + content[index:]
    mapFiles[fileName] = content


def tagParagraphs(fileName):
    paragraphs = mapContent[fileName].split("\n\n")

    for paragraph in paragraphs:
        # Tag paragraph if it is true
        if hasVerb(paragraph):
            paragraph = paragraph
            position = mapFiles[fileName].find(paragraph)
            tag(position, paragraph, fileName, "paragraph")
            tagSentences(paragraph, fileName)
        # else:
        #     print(paragraph)
        #     print('IS NOT PARAGRAPH')
    # End method for paragraph tagging
    return


def hasVerb(text):
    words = nltk.word_tokenize(text)

    # If there is no verb, it's not a paragraph
    for word, part in nltk.pos_tag(words):

        if part[0] == 'V':
            return True
            break

    return False


def tagSentences(paragraph,fileName):
    sentences = nltk.sent_tokenize(paragraph)

    for sentence in sentences:
        if hasVerb(sentence):
            sentence = sentence.strip()
            position = mapFiles[fileName].find(sentence)
            tag(position, sentence[:-1], fileName, "sentence")

    return


def getTopic(fileName):
    # Tag topic from headers
    headerHint = "Topic:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])
    # If header topic is not found
    if temp is None:
        return

    headerTopic = temp.group(1).strip()
    mapTags[fileName]['topic'] = headerTopic
    topics.append(headerTopic)
    return

def getType(fileName):
    # Tag topic from headers
    headerHint = "Type:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])
    # If header topic is not found
    if temp is None:
        return

    headerType = temp.group(1).strip()
    mapTags[fileName]['type'] = headerType
    types.append(headerType)
    return

def findHeaderLocation(fileName):
    # Tag start and end time from headers
    headerHint = "Place:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])
    # If header topic is not found
    if temp is None:
        return

    line = temp.group(1).strip()

    return line


def tagLocation(fileName):
    tagLength = len("<location></location>")

    for location in locations:
        counter = 0
        # print(fileName, location)
        for loc in re.finditer(location, mapFiles[fileName]):
            index = loc.start() + counter * tagLength
            loc = loc.group().strip()
            tag(index, loc, fileName, 'location')
            counter = counter + 1

    return


def findHeaderSpeaker(fileName):
    # Tag start and end time from headers
    headerHint = "Who:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    # If header times are not found
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
    # Tag start and end time from headers
    headerHint = "Time:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    # If header times are not found
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

    # Find times in content
    time_format2 = re.compile(r"\b((0?[1-9]|1[012])([:.][0-5][0-9])?(\s?[apAP][Mm])|([01]?[0-9]|2[0-3])([:.][0-5][0-9]))\b")
    time_format = re.compile("\\b((1[0-2]|0?[1-9])(([:.][0-5][0-9])?)(\s?)([AaPp][Mm])|(1[0-2]|0?[1-9])([:.][0-5][0-9])){1}")

    # Check how many positions have advanced
    counter = 0
    tagLength = len("<stime></stime>")

    # Add tags at start and end of time
    # ignore = "PostedBy:(.*)"
    # ignoreLine = re.search(ignore, mapFiles[fileName]).group().strip()
    # content = mapFiles[fileName].replace(ignoreLine, '')
    # contentTimes = time_format.finditer(content)
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
        # else:
        #     mapTags[fileName]['stime'] = word
        #     tag(index, word, fileName, 'stime')
        #     counter = counter + 1

    return


def printTaggedFiles():
    # Empty the output folder
    emptyOutputFolder("output/")

    for file in mapFiles:
        outputFilePath =  "output/" + file
        out = open(outputFilePath, 'w')
        print(mapFiles[file], end="", file=out)

    return


if __name__ == '__main__':
    # Read the file contents from the 'untagged' folder
    print('Tagging files...')
    emptyOutputFolder("output/")
    readContents()

    # Set the file name
    file = "302.txt"

    # Initialise key for hash map tags
    for fileName in mapFiles:
        mapTags[fileName] = {}

        # Tag in order
        tagParagraphs(fileName)
        tagLocation(fileName)
        tagSpeaker(fileName)
        tagTime(fileName)
        getTopic(fileName)
        getType(fileName)

    printTaggedFiles()
    print('Finished tagging files')

    for topic in types:
        print(topic)
