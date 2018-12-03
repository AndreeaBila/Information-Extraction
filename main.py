import nltk

from os import listdir
from os.path import isfile, join

# Declarations of hash map for files and tag details
mapFiles    = {}
mapHeaders  = {}
mapContent  = {}
mapTags     = {}

def readContents():
    myPath = "wsj_untagged/";
    onlyfiles = [f for f in listdir(myPath) if isfile(join(myPath, f))]

    # corpus_root = '/Users/andre/nltk_data/corpora/wsj_untagged/'

    # Read each file
    for fileName in onlyfiles:
        # Construct file name and read the file
        filePath = myPath + fileName
        file = open(filePath, "r")
        fileContent = file.read()

        # Map file content by file name
        mapFiles[fileName] = fileContent

    for content in mapFiles:
        print(mapFiles[content])

# if __name__ == '__main__':
#     print("Hello world!")


readContents()