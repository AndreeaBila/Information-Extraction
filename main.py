import nltk
import numpy
import re
import os
from os import listdir
from os.path import isfile, join
from nltk.tokenize import word_tokenize
from nltk import ne_chunk
from nltk.tag import StanfordNERTagger

# Declarations of hash map for files and tag details
mapFiles    = {}
mapHeaders  = {}
mapContent  = {}
mapTags     = {}
# nltk.download();
def readContents():
    myPath = "untagged/";
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
    for file in mapFiles:
        f = mapFiles[file]
        if "Abstract: " in f:
            temp = f.split("Abstract: ")
            header = temp[0]
            text = temp[1]
            # text = text.strip()

            time = 'time'
            posted = header.lower().find("postedby")
            time_header = header.lower().find(time)
            if time_header != -1:
                if posted != -1:
                    toreplace = header[time_header:posted]
                else:
                    toreplace = header[time_header :]

                header = header.replace(toreplace, tagTime(toreplace))

            text = tagTime(text)
            text = tagSpeaker(text)

            d = "\n\n"
            paragraphs = [e+d for e in text.split(d) if e]
            par_tagged = []


            for par in paragraphs:
                par_tagged.append(tagParagraph(par))

            mapHeaders[file] = header
            mapContent[file] = par_tagged

            out = open("res.txt", "w")

            if file == "301.txt":
                print(mapHeaders[file].rstrip())
                print("Abstract: \n")
                for par in mapContent[file]:
                    # print(par + "\n")
                    print(par + '\n')

def tagSpeaker(text):
    stanfordClassifier = 'C:/Users/andre/nltk_data/taggers/stanford-ner-2018-10-16/classifiers/english.muc.7class.distsim.crf.ser.gz'
    stanfordNerPath = 'C:/Users/andre/nltk_data/taggers/stanford-ner-2018-10-16/stanford-ner.jar'
    st = StanfordNERTagger(stanfordClassifier, stanfordNerPath, encoding='utf8')
    result = st.tag(word_tokenize(text))
    res = []
    for r in result:
        if r[1] == "PERSON":
            res.append(r[0])

    if len(res) > 1:
        tagged = "<speaker>" + res[0] + " " + res[1] + "</speaker>"
        text = text.replace(res[0] + " " + res[1], tagged)
    else:
        if len(res) > 0:
            tagged = "<speaker>" + res[0] + "</speaker>"
            text = text.replace(res[0] + res[1], tagged)

    return text


def tagTime(text):
    # time_format1 = re.compile(r"(24:00|2[0-3]:[0-5][0-9]|[0-1][0-9]:[0-5][0-9])")
    time_format2 = re.compile(r"\b((0?[1-9]|1[012])([:.][0-5][0-9])?(\s?[apAP][Mm])|([01]?[0-9]|2[0-3])([:.][0-5][0-9]))\b")

    times = time_format2.findall(text)
    if len(times) > 0:
        time1 = '<stime>' + times[0][0] + "</stime>"
        text = text.replace(times[0][0], time1)
    if len(times) > 1:
        time2 = '<etime>' + times[1][0] + "</etime>"
        text = text.replace(times[1][0], time2)


    # for t in times:
    #     if len(times) == 2:
    #     time = '<stime>' + t[0] + "</stime>"
    #     text = text.replace(t[0], time)
    #     print(time)

    return text


def tagTime2(fileName):
    # Tag start and end time from headers
    headerRegEx = "Time:(.*)"
    headerTimesTemp = re.search(headerRegEx, mapHeaders[fileName])

    # If header times are not found
    if headerTimesTemp is None:
        return

    headerTimes = headerTimesTemp.group(1).split("-")

    if len(headerTimes) == 1:
        mapTags[fileName]['stime'] = headerTimes[0].strip()
        mapTags[fileName]['etime'] = "PARAMETER_EMPTY"
    elif len(headerTimes) == 2:
        mapTags[fileName]['stime'] = headerTimes[0].strip()
        mapTags[fileName]['etime'] = headerTimes[1].strip()
    else:
        mapTags[fileName]['stime'] = "PARAMETER_EMPTY"
        mapTags[fileName]['etime'] = "PARAMETER_EMPTY"

    # Find times in content
    timeRegEx = re.compile("\\b((1[0-2]|0?[1-9])((:[0-5][0-9])?)(\s?)([AaPp][Mm])|(1[0-2]|0?[1-9])(:[0-5][0-9])){1}")

    # Check how many positions have advanced
    counter = 0
    TIME_TAG_LEN = len("<stime></stime>")

    # Add tags at start and end of time
    for m in timeRegEx.finditer(mapFiles[fileName]):
        position = m.start() + counter * TIME_TAG_LEN
        wordToTag = m.group().strip()
        if wordToTag.lower() == mapTags[fileName]['stime'].lower():
            tag(position, wordToTag, fileName, 'stime')
            counter += 1
        elif wordToTag.lower() == mapTags[fileName]['etime'].lower():
            tag(position, wordToTag, fileName, 'etime')
            counter += 1

    # End method for time tagging
    return


def tagSentence(sentence):
    return "<sentence>" + sentence + "</sentence>"


def tagParagraph(paragraph):
    par_sentences = []
    sentences = nltk.sent_tokenize(paragraph)
    tagged = ""

    for sentence in sentences:
        if isSentence(sentence):
            tagged = tagged + tagSentence(sentence)
        else:
            tagged = tagged + sentence


    par_sentences.append("")
    par_sentences.append(tagged)

    for par in par_sentences:
        if "<sentence>" in par:
            tagged = "<paragraph>" + par + "</paragraph>"
        else:
            tagged = par

    # if "<sentence>" in tagged:
    #     return "<paragraph>" + tagged + "</paragraph>"

    return tagged


def isSentence(sentence):
    # if sentence.isupper():
    #     sentence=sentence.lower()

    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    for tag in tagged:
        if "VB" in tag[1]:
            return True;
    return False;


def isParagraph(paragraph):
    sentences = nltk.sent_tokenize(paragraph)
    for sen in sentences:
        if not isSentence(sen):
            return False;
    return True;

        # text =
        # sentences = nltk.sent_tokenize(text)
        # tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        # tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        # for sent in tagged_sentences:
        #     print (nltk.ne_chunk(sent))
        # text_tagged = ""
        # for sent in sentences:
        #     text_tagged = text_tagged + "<sentence>" + sent + "</sentence>"
        # print(text_tagged)

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
# print(tagTime("Time:     3:30 PM - 5:00 PM"))
# print(tagSpeaker("Path replanning"))
# print(tagSpeaker(" WHO:  Ramesh Bollapragada, Graduate student, GSIA/Robotics Program WHERE: 4623 WEAN HALL WHEN: Friday, Oct 7 at 1pm TITLE: AN ASYNCHRONOUS TEAM SOLUTION TO SCHEDULING STEEL PLANTS IN DIRECT HOT CHARGE MODE In this talk, I will address the problem of direct hot charge scheduling of steel rolling mills in the primary steel making area (continous caster and hot strip mill). The work involved scheduling a huge order book (of approximately 5000 orders) with the objective of minimizing the operating costs, tardiness and inventory. This is a combinatorial problem due to complex constraints built into it. We proposed an asynchronous team solution for this domain. The intial schedules were generated by two different construction algorithms whose performance on the objective function was different from each other. I will present some preliminary results which show significant improvements in the evaluation costs when the above designs are integrated in the framework of ATeams. This research was carried out at IBM's T.J. Watson Research Center over the summer of 1994. This work was performed jointly with  Dr.Sesh Murthy of IBM."))