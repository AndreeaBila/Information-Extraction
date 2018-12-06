from os import listdir
from os.path import isfile, join
from utilities import emptyOutputFolder
import nltk
import re

mapFiles    = {}
mapHeaders  = {}
mapContent  = {}
mapTags     = {}

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
        if isParagraph(paragraph):
            position = mapFiles[fileName].find(paragraph)
            tag(position, paragraph.rstrip(), fileName, "paragraph")
            tagSentences(paragraph)
        # else:
        #     print(paragraph)
        #     print('IS NOT PARAGRAPH')
    # End method for paragraph tagging
    return


def isParagraph(text):
    words = nltk.word_tokenize(text)

    # If there is no verb, it's not a paragraph
    for word, part in nltk.pos_tag(words):

        if part[0] == 'V':
            return True
            break

    return False


def tagSentences(paragraph):
    sentences = nltk.sent_tokenize(paragraph)

    for sentence in sentences:
        position = mapFiles[fileName].find(sentence)
        tag(position, sentence, fileName, "sentence")

    return


def tagTopic(fileName):
    # Tag topic from headers
    headerHint = "Topic:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])
    # If header topic is not found
    if temp is None:
        return

    headerTopic = temp.group(1).strip()
    mapTags[fileName]['topic'] = headerTopic
    #
    # # Check how many positions have advanced
    # counter = 0
    # tagLength = len("<topic></topic>")
    #
    # # Add tags for topic
    # for topic in re.finditer(headerTopic, mapFiles[fileName]):
    #     index = topic.start() + counter * tagLength
    #     tag(index, topic.group().strip(), fileName, 'topic')
    #     counter = counter + 1

    return


def tagLocation(text):
    return "Not Implemented"


def tagSpeaker(fileName):
    # Tag start and end time from headers
    headerHint = "Who:(.*)"
    temp = re.search(headerHint, mapHeaders[fileName])

    # If header times are not found
    if temp is None:
        return

    line = temp.group(1).strip()
    temp2 = re.split(',|/|-|\(', line)
    name = temp2[0]
    print(fileName + " " + name)

    mapTags[fileName]['speaker'] = name

    # Check how many positions have advanced
    counter = 0
    tagLength = len("<speaker></speaker>")

    # Add tags for topic
    for n in re.finditer(name, mapFiles[fileName]):
        index = n.start() + counter * tagLength
        tag(index, n.group().strip(), fileName, 'speaker')
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
    time_format = re.compile("\\b((1[0-2]|0?[1-9])((:[0-5][0-9])?)(\s?)([AaPp][Mm])|(1[0-2]|0?[1-9])(:[0-5][0-9])){1}")

    # Check how many positions have advanced
    counter = 0
    tagLength = len("<stime></stime>")

    # Add tags at start and end of time
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
        else:
            mapTags[fileName]['stime'] = word
            tag(index, word, fileName, 'stime')
            counter = counter + 1

    return


def printTaggedFiles():

    for file in mapFiles:
        outputFilePath =  "output/" + file[:-4] + "_tagged.txt"
        out = open(outputFilePath, 'w')
        print(mapFiles[file], end="", file=out)

    return

if __name__ == '__main__':

    # printTaggedFiles()

    # Read the file contents from the 'untagged' folder
    readContents()

    # Empty the output folder
    emptyOutputFolder("output/")

    # Set the file name
    file = "301.txt"

    # Initialise key for hash map tags
    for fileName in mapFiles:
        mapTags[fileName] = {}

        # Tag in order
        tagParagraphs(fileName)
        tagTopic(fileName)
        tagLocation(fileName)
        tagSpeaker(fileName)
        tagTime(fileName)

    # Print content
    print(mapFiles[file])
    printTaggedFiles()
