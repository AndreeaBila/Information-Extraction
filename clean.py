from os import listdir
from os.path import isfile, join
from utilities import emptyOutputFolder

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

# def tag():

def printTaggedFiles():
    for file in mapFiles:
        outputFilePath =  "output/" + file[:-4] + "_tagged.txt"
        out = open(outputFilePath, 'w')
        print(mapHeaders[file], end="", file=out)
        print("Abstract", end="", file=out)
        print(mapContent[file], end="", file=out)


if __name__ == '__main__':
    readContents()
    emptyOutputFolder("output/")
    # printTaggedFiles()