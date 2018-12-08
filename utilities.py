import os, shutil
from os import listdir
from os.path import isfile, join
import re

def emptyOutputFolder(folder):
    for file in os.listdir(folder):
        filePath = os.path.join(folder, file)
        try:
            if os.path.isfile(filePath):
                os.unlink(filePath)
        except Exception as e:
            print(e)
