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
import tweepy
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

import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import io
import plotly.express as px

import unittest

from compare_gui import *


def api_view(keyword ,since ,until) :             # ตรวจสอบเเละเพิ่มข้อมูล tweet ในกรณีที่มีวันที่ไม่มีข้อมูล

    start = datetime.strptime(since ,'%Y-%m-%d')
    end = datetime.strptime(until ,'%Y-%m-%d')

    time_conditional = (datetime.now() - timedelta(days = 6)).strftime("%Y-%m-%d")
    limit = datetime.strptime(time_conditional ,'%Y-%m-%d')
    date_time = time_conditional
 
    try :
        data_file = pandas.read_csv(str(keyword) + '_api.csv')
        if (int((limit - start).days) > 0) or (int((limit - end).days) > 0) :
            if (int((limit - start).days) > 0) and (int((limit - end).days) <= 0) :
                con1 = data_file['time'] >= f'{date_time} 00:00:00'
                con2 = data_file['time'] <= f'{until} 23:59:59'
                compare = data_file[con1 & con2]
                no_data = time_check(date_time,until,compare)
                print("len data = " ,no_data)

                if len(no_data) == 0 :
                    pass
                else :
                    api_search = Data_twitter(str(keyword))
                    for each_date in no_data :
                        time_use = datetime.strptime(each_date ,'%Y-%m-%d') + timedelta(days = 1)
                        time_input = time_use.strftime("%Y-%m-%d")
                        api_search.get_data_by_time(time_input)
            else :
                endnable_time = datetime.now().strftime("%Y-%m-%d")
                con1 = data_file['time'] >= f'{date_time} 00:00:00'
                con2 = data_file['time'] <= f'{endnable_time} 23:59:59'
                compare = data_file[con1 & con2]
                no_data = time_check(date_time,endnable_time,compare)
                print("len data = " ,no_data)

                if len(no_data) == 0 :
                    pass
                else :
                    api_search = Data_twitter(str(keyword))
                    for each_date in no_data :
                        time_use = datetime.strptime(each_date ,'%Y-%m-%d') + timedelta(days = 1)
                        time_input = time_use.strftime("%Y-%m-%d")
                        api_search.get_data_by_time(time_input)
        else :
            con1 = data_file['time'] >= f'{since} 00:00:00'
            con2 = data_file['time'] <= f'{until} 23:59:59'
            compare = data_file[con1 & con2]
            no_data = time_check(since,until,compare)
            print("len data = " ,no_data)
            
            if len(no_data) == 0 :
                pass
            else :
                api_search = Data_twitter(str(keyword))
                for each_date in no_data :
                    time_use = datetime.strptime(each_date ,'%Y-%m-%d') + timedelta(days = 1)
                    time_input = time_use.strftime("%Y-%m-%d")
                    api_search.get_data_by_time(time_input)

    except (FileNotFoundError , pandas.errors.EmptyDataError) :
        if (int((limit - start).days) > 0) or (int((limit - end).days) > 0) :
            if (int((limit - start).days) > 0) and (int((limit - end).days) <= 0) :
                limited = limit + timedelta(days = 1)
                break_time = end + timedelta(days = 1)
                api_search = Data_twitter(str(keyword))
                while int((break_time - limited).days) >= 0 :
                    time_input = break_time.strftime("%Y-%m-%d")
                    api_search.get_data_by_time(time_input)
                    break_time -= timedelta(days = 1)
            else :
                api_search = Data_twitter(str(keyword))
                api_search.get_data()
        else :
            run_time = start + timedelta(days = 1)
            break_time = end + timedelta(days = 1)
            api_search = Data_twitter(str(keyword))
            while int((break_time - run_time).days) >= 0 :
                time_input = run_time.strftime("%Y-%m-%d")
                api_search.get_data_by_time(time_input)
                run_time += timedelta(days = 1)


    #- - - - - - - - - - - - - unit test - - - - - - - - - - - - - - - - -
    test_list = []
    data_test = pandas.read_csv(str(keyword) + '_api.csv')
    con_test1 = data_test['time'] >= f'{since} 00:00:00'
    con_test2 = data_test['time'] <= f'{until} 23:59:59'
    compare_test = data_test[con_test1 & con_test2]
    for test in compare_test['tweet'] :
        test_list.append(test)
    return len(test_list)



#_________________________________________________________________________________________________________________________________________________________

class Data_twitter() :              # class สำหรับการดึงข้อมูลมาจาก twiter
    def __init__(self,keyword) :

        self.keyword = keyword
        self.tweet_mode = "extended"
        self.result_type = "mixed"
        self.count = 100

        self.tweet_key = 'VxMCWFlpMKTXhBESQTOh08r2o'
        self.tweet_secret_key = 'z0hqQIGvoCMY3k9PPGQXEVX3hpc4rUBNojYC969SfDKkuxTV22'
        self.tweet_token = '1349224938192789504-k79UIhvhgNvPB2jK8310B02uSCz3oE'
        self.tweet_secret_token = 'atzvoIHYVAQjZoKxEqZeoDg2Wx2ITBctifbMRTWT86u5a'

        self.auth = tweepy.OAuthHandler(self.tweet_key, self.tweet_secret_key)
        self.auth.set_access_token(self.tweet_token, self.tweet_secret_token)

        self.api = tweepy.API( self.auth,wait_on_rate_limit=False,wait_on_rate_limit_notify=False)

        self.old_data = self.back_up(keyword)

    def get_data(self) :          # function สำหรับการดึงข้อมูลมาจาก twiter โดยถึงข้อมูลเเบบ real time
        self.test = None
        count_limit = 5
        count = 0
        maxip = 0
        while count < count_limit :
            try :
                name_file = str(self.keyword) + '_api.csv'
                self.make_file = open(name_file, 'a', newline='', encoding='utf-8')
                fieldnames = ['places', 'time', 'tweet']
                self.writer = csv.DictWriter( self.make_file, fieldnames=fieldnames )
                self.writer.writeheader()

                data = self.api.search(q= self.keyword,
                                    count= self.count,
                                    tweet_mode= self.tweet_mode,
                                    result_type= self.result_type,
                                    max_id= str(maxip - 1))

                self.test = data
                self.file_manage(data)
                if len(data) == 0 :
                    continue

                maxip = data[-1].id
                count += 1

            except tweepy.RateLimitError : 
                print('Over limit rate')
                break
                
        print("Done",count)


    def get_data_by_time(self,date_time) :           # function สำหรับการดึงข้อมูลมาจาก twiter โดยถึงข้อมูลตามช่วงเวลา
        self.test = None
        count_limit = 5
        count = 0
        maxip = 0
        while count < count_limit :
            try :
                name_file = str(self.keyword) + '_api.csv'
                self.make_file = open(name_file, 'a', newline='', encoding='utf-8')
                fieldnames = ['places', 'time', 'tweet']
                self.writer = csv.DictWriter( self.make_file, fieldnames=fieldnames )
                self.writer.writeheader()

                if maxip == 0 :
                    data = self.api.search(q= self.keyword,
                                        count= self.count,
                                        tweet_mode= self.tweet_mode,
                                        result_type= self.result_type,
                                        until = date_time)

                else :
                    data = self.api.search(q= self.keyword,
                                        count= self.count,
                                        tweet_mode= self.tweet_mode,
                                        result_type= self.result_type,
                                        until = date_time,
                                        max_id= str(maxip - 1000000))

                self.test = data
                self.file_manage(data)
                if len(data) == 0 :
                    continue

                maxip = data[-1].id
                count += 1

            except tweepy.RateLimitError : 
                print('Over limit rate')
                break
                
        print("Done",count)


    def file_manage(self,data) :             # function สำหรับการบันทึกข้อมูลลงใน data file โดยมีการป้องกันการบันทึกข้อมูลซ้ำ
        for information in data:
            if(  (not information.retweeted) and ("RT @" not in information.full_text)  ):
                if information.full_text not in self.old_data :
                    self.writer.writerow( {'places': information.user.location, 'time': str(information.created_at), 'tweet':information.full_text} )

    def back_up(self,keyword) :             # function สำหรับการอ่านข้อมูลใน data file ลงในตัวของ class เพื่อนำไปตรวจสอบกับข้อมูลใหม่ว่าซ้ำหรือไม่
        store = []
        try :
            old_file = pandas.read_csv(str(keyword) + '_api.csv')
            for tweet in old_file['tweet'] :
                store.append(tweet)
            return store
        except pandas.errors.EmptyDataError :
            return store
        except FileNotFoundError :
            return store

    def time_funtion(self,start_time,end_time) :            # function สำหรับการ format เวลา
        start = datetime.strptime(start_time ,'%Y-%m-%d')
        end = datetime.strptime(end_time ,'%Y-%m-%d')
        start_point = start + timedelta(days = 1)
        end_point = end + timedelta(days = 1)
        while int((end_point - start_point).days) != -1 :
            timestampStr = start_point.strftime('%Y-%m-%d')
            self.get_data_by_time(timestampStr)
            start_point = start_point + timedelta(days = 1)


#_________________________________________________________________________________________________________________________________________________________

def top_trends_tweet() :      # function สำหรับการดึงข้อมูล top trends tweet มาจาก twiter

    tweet_key = 'VxMCWFlpMKTXhBESQTOh08r2o'
    tweet_secret_key = 'z0hqQIGvoCMY3k9PPGQXEVX3hpc4rUBNojYC969SfDKkuxTV22'
    tweet_token = '1349224938192789504-k79UIhvhgNvPB2jK8310B02uSCz3oE'
    tweet_secret_token = 'atzvoIHYVAQjZoKxEqZeoDg2Wx2ITBctifbMRTWT86u5a'

    auth = tweepy.OAuthHandler(tweet_key, tweet_secret_key)
    auth.set_access_token(tweet_token, tweet_secret_token)

    api = tweepy.API( auth,wait_on_rate_limit=False,wait_on_rate_limit_notify=False)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    name_file = 'top_trends_tweet.csv'
    csvfile = open(name_file, 'w', newline='', encoding="utf-8")

    fieldnames = ['trends', 'tweet_number']
    writer = csv.DictWriter( csvfile, fieldnames=fieldnames )
    writer.writeheader()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    location_id = 1225448

    all_trends = api.trends_place(id = location_id)

    for data in all_trends :
        for trend in data['trends'] :
            if trend['tweet_volume'] != None :
                writer.writerow( {'trends': trend['name'], 'tweet_number': trend['tweet_volume']} )

    csvfile.close()

    #- - - - - - - - - - - - - unit test - - - - - - - - - - - - - - - - -
    test_list = []
    data_test = pandas.read_csv(name_file)
    for test in data_test['trends'] :
        test_list.append(test)
    return len(test_list)

#________________________________________________________________________________________________________________________________________________________



class NLP() :                       # class สำหรับการตัดคำเเละจัดอันดับคำจาก twiter
    def __init__(self ,keyword ,message_file) :
        
        self.keyword = keyword
        # ----------------------read file------------------------------------
        name_file = str(keyword) + '_NLP.csv'
        self.csvfile_output = open(name_file, 'w', newline='', encoding="utf-8")
        self.input_file = message_file

        fieldnames = ['word', 'number']
        self.writer_output = csv.DictWriter( self.csvfile_output, fieldnames=fieldnames )
        self.writer_output.writeheader()
        # ----------------------NLP thai------------------------------------
        with codecs.open("stopwords_th.txt", "r", "utf-8") as t :
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

        # ----------------------detector--------------------------------------------
        self.nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
        # ------------------------------------------------------------------
        self.all_word = {}
        for sentence in self.input_file['tweet'] :
            if (self.detection_lang(sentence) == "en") or (self.detection_lang(sentence) == "th") :
                self.main_function(sentence)

        self.all_word = self.word_rank(self.all_word)
        for temp in self.all_word :
            self.writer_output.writerow({'word':temp, 'number': self.all_word[temp]})

        self.csvfile_output.close()

    def main_function(self, datas):           # function สำหรับการนำประโยคมาตัดคำเเละเก็บประโยคที่ตัดคำเเล้วมาเก็บเป็น list

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
        for i in proc :
            # ----------------special symbol------------------
            special = re.compile(r"\W+").sub("",i) # special symbol
            if(special == "" or i.lower() == "https" or i.lower() == "http"):
                continue
            # ------------------------------------------------

            # -------------- stop word thai and english --------------
            if i.lower() != str(self.keyword) :
                if(isthai(i)):
                    if( i not in self.stopwords_thai ) and ( i not in self.stopwords_thai_2) :
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

    def detection_lang(self, data) :       # function สำหรับการตรวจสอบภาษาประโยคว่าเป็นภาษาอะไร
        doc = self.nlp(data)
        return doc._.language["language"]

    def word_rank(self, data) :            # function สำหรับการนำประโยคที่ตัดคำมาเเล้วมานับว่าเเต่ละคำใน 1 ประโยคมีกี่ตัวเเละนำไปจัด rank
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

#________________________________________________________________________________________________________________________________________________________

def time_check(start,end,data_file) :      # function สำหรับตรวจสอบว่าข้อมูล data frame ที่เราเลือกมาตามช่วงเวลานั้นมีครบทุกวันหรือไม่ถ้าไม่ขาดวันไหนบ้าง
    date_start = datetime.strptime(start ,'%Y-%m-%d')
    date_end = datetime.strptime(end ,'%Y-%m-%d')

    day_list = []
    day_file = []
    usable_date = []

    while int((date_end - date_start).days) >= 0 : 
        day_list.append(date_start.strftime('%Y-%m-%d'))
        date_start +=  timedelta(days = 1)

    for date in data_file['time'] :
        if date[:10] not in day_file :
            day_file.append(date[:10])

    for date in day_list :
        if date not in day_file :
            usable_date.append(date)

    return usable_date

#________________________________________________________________________________________________________________________________________________________

def geopy2(data_frame) :          # function สำหรับเเปลง location ต่างๆที่อยู่ใน data frame เป็นพิกัด
    test_list = []

    geolocator = Nominatim(user_agent="sample app")
   
    name_file = 'coordinates_file.csv'
    make_file = open(name_file, 'w', newline='', encoding='utf-8')
    fieldnames = ['address','location','latitude','longitude']
    writer = csv.DictWriter( make_file, fieldnames = fieldnames )
    writer.writeheader()

    for massage in data_frame['places'].dropna() :
        try:
            data = geolocator.geocode(str(massage))

            writer.writerow( {'address' : massage, 'location' : data, 'latitude' : data.point.latitude, 'longitude' : data.point.longitude} )
            test_list.append((massage, data.point.latitude, data.point.longitude))
            print("2")

        except AttributeError:
            print('3')
    make_file.close()
    return test_list

#________________________________________________________________________________________________________________________________________________________

def plotly() :                # function สำหรับนำพิกัดต่างๆไป plot ในเเผนที่โลกเเล้ว save รูปดังกล่าว

    name = 'coordinates_file.csv'
    df = pandas.read_csv(str(name))

    fig = px.scatter_geo(df, 
                        # longitude is taken from the df["lon"] columns and latitude from df["lat"]
                        lon = "longitude", 
                        lat = "latitude", 
                        # choose the map chart's projection
                        projection="natural earth",
                        # columns which is in bold in the pop up
                        hover_name = "address",
                        # format of the popup not to display these columns' data
                        hover_data = {"address":False,
                                    "longitude": False,
                                    "latitude": False})

    # scatter_geo allow to change the map date based on the information from the df dataframe, but we can separately specify the values that are common to all
    # change the size of the markers to 25 and color to red
    fig.update_traces(marker=dict(size=25, color="red"))
    # fit the map to surround the points
    fig.update_geos(fitbounds = "locations", showcountries = True)
    # add title
    fig.update_layout(title = 'coordinates')
    fig.write_image("coordinates_file.png")
    #fig.show()

#_________________________________________________________________________________________________________________________________________________________


if __name__ == '__main__':

    """class MyTest(unittest.TestCase):
        def test_api_view_world(self):
            myCal = api_view("covid" ,"2021-03-24" ,"2021-03-31")
            self.assertIsNotNone(myCal)
 
    unittest.main()"""

    top_trends_tweet()
    o = pandas.read_csv('top_trends_tweet.csv').sort_values(by = "tweet_number" ,ascending = False)
    for i,j in zip(o['trends'], o['tweet_number']) :
        print(str(i) + ' : ' + str(j))