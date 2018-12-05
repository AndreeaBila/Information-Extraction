import nltk
import numpy

import os
from os import listdir
from os.path import isfile, join
from nltk.tokenize import word_tokenize
from nltk import ne_chunk

# Declarations of hash map for files and tag details
mapFiles    = {}
mapHeaders  = {}
mapContent  = {}
mapTags     = {}
# nltk.download();
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

    # for content in mapFiles:
    text = mapFiles['wsj_0001.txt']

    sentences = nltk.sent_tokenize(text)

    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    # for sent in tagged_sentences:
    #     print (nltk.ne_chunk(sent))
    text_tagged = ""
    for sent in sentences:
        text_tagged = text_tagged + "<sentence>" + sent + "</sentence>"
    print(text_tagged)

    # paragrafs =

    # print(nltk.pos_tag(tokens))
    # print(ne_chunk(nltk.pos_tag(tokens), binary=False))

    # from nltk.tag.stanford import POSTagger
    # stan_tagger = POSTagger('models/english-bidirectional-distdim.tagger', 'standford-postagger.jar')
    #
    # stan_tagger.tag(tokens)

# if __name__ == '__main__':
#     print("Hello world!")

readContents()