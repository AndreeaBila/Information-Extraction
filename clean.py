from os import listdir
from os.path import isfile, join
from utilities import emptyOutputFolder
import nltk

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
        if isParagraph(paragraph) == True:
            position = mapFiles[fileName].find(paragraph)
            tag(position, paragraph.rstrip(), fileName, "paragraph")
            tagSentences(paragraph)

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


def tagTopic(text):
    return "Not Implemented"


def tagLocation(text):
    return "Not Implemented"


def tagSpeaker(fileName):
    # if "who:" in mapFiles[fileName].lower():
        
    return "Not Implemented"


def tagTime(text):
    return "Not Implemented"


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
    fileName = "302.txt"

    # Initialise key for hash map tags
    mapTags[fileName] = {}

    # Tag in order
    tagParagraphs(fileName)
    tagTopic(fileName)
    tagLocation(fileName)
    tagSpeaker(fileName)
    tagTime(fileName)

    # Print content
    print(mapFiles[fileName])
