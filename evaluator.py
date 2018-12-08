import re
from os import listdir
from os.path import isfile, join

def readContents():
    myPath = "output/"
    files = [f for f in listdir(myPath) if isfile(join(myPath, f))]
    return files

def evaluate():
    return "Not implemented"

if __name__ == "__main__":
    evaluate()