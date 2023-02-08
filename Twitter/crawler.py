import requests
from bs4 import BeautifulSoup, SoupStrainer
import csv
import pandas
from pandas_datareader import data as pdr
import re
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from pythainlp.corpus.common import thai_words
from pythainlp import word_tokenize, Tokenizer
from pythainlp.tokenize import word_tokenize
from pythainlp.util import isthai
from pythainlp.corpus import *
import pythainlp
import spacy
from nltk.corpus import stopwords
from spacy.lang.en.stop_words import STOP_WORDS
from spacy_langdetect import LanguageDetector
from spacy.matcher import Matcher
import emoji
import time
from datetime import*
import shutil
from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta
from textblob import TextBlob
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as plt_date

import pickle 
import codecs
from itertools import chain
from nltk import NaiveBayesClassifier as nbc

from twiter_api import*
#from test_11 import*


class sentiment() :        # class สำหรับการนำประโยคเเต่ละประโยคมาวิเคราะห์เเนวโน้มว่าเป็นประโยคในด้านบวกหรือลบหรือปกติ
    def __init__(self):
        # ----------------------NLP thai------------------------------------

        with codecs.open("stopwords_th.txt", "r", "utf-8") as t:
            lines = t.readlines()
        stop_thai = [e.strip() for e in lines]
        del lines
        t.close() # ปิดไฟล์

        self.stopwords_thai = pythainlp.corpus.common.thai_stopwords()
        self.stopwords_thai_2 = stop_thai
        modul= self.loadData()
        self.classifier = modul[0]
        self.vocabulary = modul[1]
        # ------------------------------------------------------------------

        # ----------------------NLP english------------------------------------
        self.nlp = spacy.load("en_core_web_md")
        self.STOP_WORD_1 = self.nlp.Defaults.stop_words # stop word ของ spacy
        self.STOP_WORD_2 = stopwords.words('english') # stop word ของ nltk
        self.STOP_WORD_3 = STOP_WORDS # stop word ของ spacy
        # ------------------------------------------------------------------

        # ----------------------detector--------------------------------------------
        self.nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
        # --------------------------------------------------------------------------
      
    def nlp_function(self, datas):     # function สำหรับการนำประโยคมาตัดคำเเละเก็บประโยคที่ตัดคำเเล้วมาเก็บเป็น list

        output_list = []
        out_STR = ""
        # --------------------------Filter all thing and return list of word "usefull"--------------------------------
        try:
            pattern  = re.compile(r"(#+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_str_hashtags = pattern.sub("", datas)

            pattern  = re.compile(r"(@+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_str_add = pattern.sub("", out_str_hashtags)

            str_output = emoji.get_emoji_regexp().sub(u'', out_str_add)

            pattern  = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
            out_str_link = pattern.sub("", str_output)  

            out_STR += out_str_link

            pattern  = re.compile(r"(?P<out_list>#+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_list = re.search(pattern, datas)
            output_list.append(out_list.group("out_list"))
 
            pattern  = re.compile(r"(?P<out_list>@+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_list = re.search(pattern, datas)
            output_list.append(out_list.group("out_list"))
        except AttributeError:
            pass
        # --------------------------Filter all thing and return list of word "usefull"--------------------------------

        proc = word_tokenize(out_STR, engine="newmm", keep_whitespace=False)
        for i in proc:
            # ----------------special symbol------------------
            special = re.compile(r"\W+").sub("",i) # special symbol
            if(special == "" or i.lower() == "https" or i.lower() == "http"):
                continue
            # ------------------------------------------------

            # -------------- stop word thai and english --------------
            if(isthai(i)):
                if ( i not in self.stopwords_thai ) and ( i not in self.stopwords_thai_2) :
                    output_list.append(i)
            elif(i.isalpha()):
                if( i.lower() not in self.STOP_WORD_1 and i.lower() not in self.STOP_WORD_2 and i.lower() not in self.STOP_WORD_3 ):
                    output_list.append(i)
            # --------------------------------------------------------
        return output_list

    def detection_lang(self, data) :       # function สำหรับการตรวจสอบภาษาประโยคว่าเป็นภาษาอะไร
        doc = self.nlp(str(data))
        return doc._.language["language"]

    def sentiment_englist(self, data_flame, key) :      # function การวิเคราะห์ sentiment สำหรับประโยคที่เป็นภาษาอังกฤษ
        positive = 0
        neutral = 0
        negative = 0
        for text in data_flame[key] :
            if self.detection_lang(text) == "en" :         # กรณีที่ตรวจสอบเเล้วว่าประโยคนี้เป็นภาษาอังกฤษ
                analysis = TextBlob(text)
                if analysis.sentiment[0] > 0 :
                    positive += 1
                elif analysis.sentiment[0] < 0 :
                    negative += 1
                else :
                    neutral += 1

            elif self.detection_lang(text) == "th":        # กรณีที่ตรวจสอบเเล้วว่าประโยคนี้เป็นภาษาไทย
                thai_nlp = self.nlp_function(text)
                result_sentiment = self.sentiment_thai(thai_nlp)
                positive += result_sentiment[0]
                neutral += result_sentiment[1]
                negative += result_sentiment[2]

        name_file = 'temp_file.csv'
        make_file = open(name_file, 'w', newline='', encoding='utf-8')
        fieldnames = ['sentiment']
        writer = csv.DictWriter( make_file, fieldnames = fieldnames )
        writer.writeheader()
        writer.writerow( {'sentiment' : positive} )
        writer.writerow( {'sentiment' : neutral} )
        writer.writerow( {'sentiment' : negative} )
        make_file.close()

        return [positive,neutral,negative]


    def sentiment_thai(self, data):               # function การวิเคราะห์ sentiment สำหรับประโยคที่เป็นภาษาไทย
        positive = 0
        neutral = 0
        negative = 0
        conditional_list = ['pos','neg','neu']
        
        featurized_test_sentence =  {i:(i in data) for i in self.vocabulary}
        type_sentence = self.classifier.classify(featurized_test_sentence) # ใช้โมเดลที่ train ประมวลผล
        if type_sentence == 'pos' :
            positive += 1
        elif type_sentence == 'neg' :
            negative += 1
        elif type_sentence == 'neu' :
            neutral += 1

        return [positive,neutral,negative]

    def storeData(self):          # function สำหรับการ update โมเดลที่ train sentiment ของภาษาไทย
        # database 
        db = Mymodul().main()
    
        # Its important to use binary mode 
        dbfile = open('Modul', 'wb') 
        
        # source, destination 
        pickle.dump(db, dbfile)                      
        dbfile.close() 
    
    def loadData(self):             # function สำหรับการ load โมเดลที่ train sentiment ของภาษาไทย
        # for reading also binary mode is important 
        dbfile = open('Modul', 'rb')      
        db = pickle.load(dbfile) 
        dbfile.close()
        return db

#_______________________________________________________________________________________________________________________________


class Mymodul() :           # class สำหรับการสร้างโมเดลที่ train sentiment ของภาษาไทย
  def main(self):

    # pos.txt
    with codecs.open('pos_thai.txt', 'r', "utf-8") as pos :
      lines = pos.readlines()
    listpos = [e.strip() for e in lines]
    del lines
    pos.close() # ปิดไฟล์

    # neg.txt
    with codecs.open('neg_thai.txt', 'r', "utf-8") as neg :
      lines = neg.readlines()
    listneg = [e.strip() for e in lines]
    del lines
    neg.close() # ปิดไฟล์

    # neutral.txt
    with codecs.open('neutral_thai.txt', 'r', "utf-8") as neutral :
      lines = neutral.readlines()
    listneutral = [e.strip() for e in lines]
    del lines
    neutral.close() # ปิดไฟล์


    pos1=['pos']*len(listpos)
    neg1=['neg']*len(listneg)
    neutral1=["neu"]*len(listneutral)

    training_data = list(zip(listpos,pos1)) + list(zip(listneg,neg1)) + list(zip(listneutral,neutral1))
  
    vocabulary = set(chain(*[word_tokenize(i[0].lower()) for i in training_data]))

    feature_set = [({i:(i in word_tokenize(sentence.lower())) for i in vocabulary},tag) for sentence, tag in training_data]
  
    classifier = nbc.train(feature_set)
    result = (classifier,vocabulary)
    return result

#_______________________________________________________________________________________________________________________________


def search_and_sentiment(keyword ,since ,until) :          # function สำหรับการนำข้อมูลออกมาจาก database โดยมี keyword เเละช่วงเวลาเป็นตัวจำกัดการดึงข้อมูลเเละนำข้อมูลไปทำ sentiment ต่อ

    all_result = {}
    pos = 0
    neu = 0
    neg = 0

    """news_file = pandas.read_csv('web_crawler.csv')
    thai_news = news_file['thai'].dropna()
    global_news = news_file['global'].dropna()
    #print(global_news)
    func_2 = sentiment()
    for news in thai_news :

        temp_name = str(news).split("https://")
        temp_name = temp_name[1][:-1].split("/")
        name_file = temp_name[0] + '_crawler.csv'

        read_data_file = pandas.read_csv(name_file)
        condition_1 = read_data_file['time'] >= f'{since} 00:00:00'
        condition_2 = read_data_file['time'] <= f'{until} 23:59:59'
        complete_file_2 = read_data_file[condition_1 & condition_2]

        head_news = complete_file_2['head_news'].str.lower()
        #print(head_news)
        head_keyword = complete_file_2[head_news.str.contains(str(keyword))]
        #print(head_keyword['content'])
        result_func_2 = func_2.sentiment_englist(head_keyword ,"content")

        pos += result_func_2[0]
        neu += result_func_2[1]
        neg += result_func_2[2]
        
        for column in head_keyword :
            all_result[column] = []
        for column in head_keyword :
            for data in head_keyword[column] :
                all_result[column].append(data)

    
    for news in global_news :
        #print(news)
        temp_name = str(news).split("https://")
        temp_name = temp_name[1][:-1].split("/")
        name_file = temp_name[0] + '_crawler.csv'

        read_data_file = pandas.read_csv(name_file)
        condition_1 = read_data_file['time'] >= f'{since} 00:00:00'
        condition_2 = read_data_file['time'] <= f'{until} 23:59:59'
        complete_file_2 = read_data_file[condition_1 & condition_2]

        head_news = complete_file_2['head_news'].str.lower()
        head_keyword = complete_file_2[head_news.str.contains(str(keyword))]
        result_func_2 = func_2.sentiment_englist(head_keyword ,"content")

        pos += result_func_2[0]
        neu += result_func_2[1]
        neg += result_func_2[2]

        for column in head_keyword :
            for data in head_keyword[column] :
                all_result[column].append(data)"""
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #- - - - - - - - - - - - เริ่มส่วนที่เเก้ - - - - - - - - - - - - - - - - - -
    day_list = []
    date_start = datetime.strptime(since ,'%Y-%m-%d')
    date_end = datetime.strptime(until ,'%Y-%m-%d')

    while int((date_end - date_start).days) >= 0 : 
        day_list.append("crawler_" + date_start.strftime('%Y-%m-%d') + "_.csv")
        date_start +=  timedelta(days = 1)
    print(day_list)
    func_2 = sentiment()
    first = True
    for news in day_list :

        try :
            read_data_file = pandas.read_csv(news)
            condition_1 = read_data_file['time'] >= f'{since} 00:00:00'
            condition_2 = read_data_file['time'] <= f'{until} 23:59:59'
            complete_file_2 = read_data_file[condition_1 & condition_2]

            head_news = complete_file_2['head_news'].str.lower()
            head_keyword = complete_file_2[head_news.str.contains(str(keyword), na=False)]
            result_func_2 = func_2.sentiment_englist(head_keyword ,"content")            # ส่วนสำหรับการส่งข้อมูลไปยัง sentiment function

            pos += result_func_2[0]
            neu += result_func_2[1]
            neg += result_func_2[2]
            
            if first :
                for column in head_keyword :
                    all_result[column] = []
                for column in head_keyword :
                    for data in head_keyword[column] :
                        all_result[column].append(data)
                first = False
            else :
                for column in head_keyword :
                    for data in head_keyword[column] :
                        all_result[column].append(data)

        except FileNotFoundError :
            pass
    #- - - - - - - - - - - - จบส่วนที่เเก้ - - - - - - - - - - - - - - - - - -
    sentiment_result = [pos ,neu ,neg]
    if len(all_result) != 0 :
        Crawler_NLP(all_result ,"content")
        return sentiment_result ,all_result

    else :
        name_file = 'Web_crawler_NLP_4.csv'
        csvfile = open(name_file, 'w', newline='', encoding="utf-8")
        fieldnames = ['word', 'number']
        writer_output = csv.DictWriter( csvfile, fieldnames = fieldnames )
        writer_output.writeheader()
        csvfile.close()
        return sentiment_result ,{"head_news" : ["No data" ], "link" : ["No data"] , "content" : ["No data"] , "time" : ["No data"] , "main_link" : ["No data"]}


#_______________________________________________________________________________________________________________________________

class Crawler_NLP() :              # class สำหรับการตัดคำเเละจัดอันดับคำจาก database ของ crawler
    def __init__(self,all_data ,head) :
        # ----------------------read file------------------------------------
        name_file = 'Web_crawler_NLP_4.csv'
        self.csvfile_output = open(name_file, 'w', newline='', encoding="utf-8")
        self.input_file = all_data

        fieldnames = ['word', 'number']
        self.writer_output = csv.DictWriter( self.csvfile_output, fieldnames=fieldnames )
        self.writer_output.writeheader()
        # ----------------------NLP thai------------------------------------
        with codecs.open("stopwords_th.txt", "r", "utf-8") as t:
            lines = t.readlines()
        stop_thai = [e.strip() for e in lines]
        del lines
        t.close() # ปิดไฟล์

        self.stopwords_thai = pythainlp.corpus.common.thai_stopwords()
        self.stopwords_thai_2 = stop_thai
        # ------------------------------------------------------------------

        # ----------------------NLP english------------------------------------
        self.nlp = spacy.load("en_core_web_md")
        self.STOP_WORD_1 = self.nlp.Defaults.stop_words 
        self.STOP_WORD_2 = stopwords.words('english') 
        self.STOP_WORD_3 = STOP_WORDS 
        # ------------------------------------------------------------------
        self.all_word = {}
        
        for sentence in self.input_file[head] :
            self.main_function(sentence)

        self.all_word = self.word_rank(self.all_word)
        for temp in self.all_word :
            self.writer_output.writerow({'word':temp, 'number': self.all_word[temp]})

        self.csvfile_output.close()

    def main_function(self, datas):            # function สำหรับการนำประโยคมาตัดคำเเละเก็บประโยคที่ตัดคำเเล้วมาเก็บเป็น list

        output_list = []
        out_STR = ""
        # --------------------------Filter all thing and return list of word "usefull"--------------------------------
        try:
            pattern  = re.compile(r"(#+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_str_hashtags = pattern.sub("", datas)

            pattern  = re.compile(r"(@+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_str_add = pattern.sub("", out_str_hashtags)

            str_output = emoji.get_emoji_regexp().sub(u'', out_str_add)

            pattern  = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
            out_str_link = pattern.sub("", str_output)  

            out_STR += out_str_link

            pattern  = re.compile(r"(?P<out_list>#+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_list = re.search(pattern, datas)
            output_list.append(out_list.group("out_list"))
 
            pattern  = re.compile(r"(?P<out_list>@+[a-zA-Z0-9(_)|ก-๙(_)0-9]{1,})")
            out_list = re.search(pattern, datas)
            output_list.append(out_list.group("out_list"))
        except AttributeError:
            pass
        # --------------------------Filter all thing and return list of word "usefull"--------------------------------

        proc = word_tokenize(out_STR, engine="newmm", keep_whitespace=False)
        for i in proc:
            # ----------------special symbol------------------
            special = re.compile(r"\W+").sub("",i) # special symbol
            if(special == "" or i.lower() == "https" or i.lower() == "http"):
                continue
            # ------------------------------------------------

            # -------------- stop word thai and english --------------
            if(isthai(i)):
                if ( i not in self.stopwords_thai ) and ( i not in self.stopwords_thai_2) :
                    output_list.append(i)
            elif(i.isalpha()):
                if( i.lower() not in self.STOP_WORD_1 and i.lower() not in self.STOP_WORD_2 and i.lower() not in self.STOP_WORD_3 ):
                    output_list.append(i)
            # --------------------------------------------------------

        for word in output_list :
            if word not in  self.all_word :
                self.all_word[word] = 1 
            else :
                self.all_word[word] += 1

    def word_rank(self, data) :        # function สำหรับการนำประโยคที่ตัดคำมาเเล้วมานับว่าเเต่ละคำใน 1 ประโยคมีกี่ตัวเเละนำไปจัด rank
        sorted_word = {}
        key = [i for i in data.keys()]
        value = [i for i in data.values()]
        for first_number in range(len(value)) :
            for second_number in range(len(value) - first_number - 1) :
                if value[first_number] <= value[first_number + second_number] :
                    value[first_number] ,value[first_number + second_number] = value[first_number + second_number] ,value[first_number]
                    key[first_number] ,key[first_number + second_number] = key[first_number + second_number] ,key[first_number]
                else :
                    pass

        for finish_sorted in range(len(data)) :
            sorted_word[key[finish_sorted]] = value[finish_sorted]

        return sorted_word



#_________________________________________________________________________________________________________________________________________________________



if __name__ == "__main__" :

    search_and_sentiment("covid" ,"2021-04-21" ,"2021-04-21")