import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string
from gtts import gTTS
import textract
import collections
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import vlc #pip install python-vlc
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def get_data(doc_file):
    if 'txt' in doc_file:
        f = open(doc_file, 'rt', encoding='utf-8', errors='ignore')
        docs = f.read()
        f.close()
    else:
        docs = textract.process(doc_file).decode('utf-8')

    return docs

def tts(docs):
    tts = gTTS(docs, lang='en')
    tts.save(BASE_DIR + '/text_classification/Recording/example.mp3')
    #get the mp3, return a playable file
    speech = vlc.MediaPlayer(BASE_DIR + '/text_classification/Recording/example.mp3')

    return speech

def extract_data(docs):
    tokens = word_tokenize(docs)
    tokens = [w.lower() for w in tokens]
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]
    #stem words for accurate graphing
    porter = PorterStemmer()
    stemmed = [porter.stem(word) for word in words]
    #extract most used words in text as indicator for topic
    wordcount = {}
    for word in stemmed:
        if word not in wordcount:
            wordcount[word]=1
        else:
            wordcount[word]+=1           
    word_counter = collections.Counter(wordcount)
    common = word_counter.most_common(3)
    result = "The top words in the text indicate the text is about " + ', '.join(str(x[0]) for x in common)

    return word_counter, result

def vis_data(word_counter):
    lst = word_counter.most_common(10)
    df = pd.DataFrame(lst, columns = ['Word', 'Count'])
    df.plot.bar(x='Word', y='Count')
    fig = plt.gcf()
    fig.savefig(BASE_DIR + "/text_classification/Images/test.png")
    img = mpimg.imread(BASE_DIR + "/text_classification/Images/test.png")

    return img #output using plt.show(img)

def runprog(doc_path):
    dataout = get_data(doc_path)
    speech = tts(dataout)
    word_count, result = extract_data(dataout)
    img = vis_data(word_count)

    return speech, img, result