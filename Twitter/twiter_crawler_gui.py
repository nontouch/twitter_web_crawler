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
import time as t
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

import concurrent.futures

from compare_gui import *
from twiter_api import *
from crawler import *
from main_menu_gui import *

class Api_and_crawler_GUI(QWidget) :     # class GUI สำหรับ twiter เเละ crawler โดยจะเเยกการทำงานระหว่างกัน
    switch_window = QtCore.pyqtSignal() 
    def __init__(self) :                 # ส่วนสำหรับการตั้งค่าหน้าต่าง GUI
        super().__init__()
        self.title = ' Twitter and web crawlerGUI '
        self.image = 'twit_bird.jpg'
        self.icon = "Shrimp-front.png"
        self.left = 300 
        self.top = 100
        self.width = 1500
        self.height = 900

        self.palette = QPalette()
        self.vbox = QVBoxLayout()

        self.tweet_dictionary = {}
        self.crawler_dictionary = {}
        
        self.api_result = []
        self.web_result = []

        self.api_rank_state = True
        self.api_sentiment_state = False

        self.web_rank_state = True
        self.web_sentiment_state = False

        self.time_and_keyword = []

        self.initUI()

    def initUI(self) :                  # ส่วนสำหรับการวาง element ต่างๆในหน้าต่าง GUI
        # ส่วนสำหรับตั้งชื่อ title เเละ set ขนาดของ GUI
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # ส่วนสำหรับวาง background ของ GUI
        background = QImage(self.image)
        background_side = background.scaled(QSize(self.width,self.height))  
        self.palette.setBrush(QPalette.Window, QBrush(background_side))
        self.setPalette(self.palette)

        #- - - - - - - - - - - - - - - - - - - - - - - - - twitter - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # ส่วนหัวข้อของ api mode ของ GUI
        self.label_api_head = QLabel(' twiter GUI ', self)
        self.label_api_head.move(625, 10)
        self.label_api_head.setFont(QFont('Arial', 30))

        # ส่วนบอกจุดที่ต้องใส่ input
        self.api_label = QLabel('keyword :', self)
        self.api_label.move(10, 80)
        self.api_label.setFont(QFont('Arial', 15))

        # ส่วนรับ input ของ api
        self.api_input = QLineEdit(self)
        self.api_input.move(125, 80)
        self.api_input.resize(350, 30)
        self.api_input.setFont(QFont('Arial', 15))

        # ปุ่มสำหรับนำ keyword เเละช่วงเวลาไปเรียกข้อมูลของ twitter
        self.api_button = QPushButton('search', self)
        self.api_button.resize(180,30)
        self.api_button.move(970,80)
        self.api_button.setFont(QFont('Times', 15)) 
        self.api_button.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ส่วน progress bar ของ api เพื่อบอกว่า code ทำ backend ของ api เสร็จหรือยัง
        self.pbar = QProgressBar(self)
        self.pbar.resize(300,30)
        self.pbar.move(1155,80)
        self.pbar.setFont(QFont('Times', 15))
        self.pbar.setValue(0)
        self.pbar.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ส่วนที่บอกว่าเวลาเริ่มต้นอยู่ไหน
        self.time_label_1 = QLabel('start :', self)
        self.time_label_1.move(500, 80)
        self.time_label_1.setFont(QFont('Arial', 15))

        # ส่วนที่บอกว่าเวลาจบอยู่ไหน
        self.time_label_2 = QLabel('end :', self)
        self.time_label_2.move(745, 80)
        self.time_label_2.setFont(QFont('Arial', 15))

        # ส่วนที่ให้เลือกเวลาเริ่มต้นที่จะเเสดงข้อมูลของ api
        time_defult = QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d")))
        self.api_time_start = QDateEdit(self)
        self.api_time_start.setMaximumDate(QtCore.QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d"))))
        self.api_time_start.setGeometry(580, 80, 150, 30)
        self.api_time_start.setDate(time_defult)
        self.api_time_start.setCalendarPopup(True)

        # ส่วนที่ให้เลือกเวลาจบที่จะเเสดงข้อมูลของ api
        self.api_time_end = QDateEdit(self)
        self.api_time_end.setMaximumDate(QtCore.QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d"))))
        self.api_time_end.setGeometry(815, 80, 150, 30)
        self.api_time_end.setDate(time_defult)
        self.api_time_end.setCalendarPopup(True)
        self.api_time_end.dateChanged.connect(lambda : self.date_limit(self.api_time_start ,self.api_time_end))

        # ส่วนที่จะเเสดงข้อมูลต่างๆของ tweet ที่เลือก
        self.output_api_label =  QTextBrowser(self)
        self.output_api_label.move(420, 120)
        self.output_api_label.resize(700,30)
        self.output_api_label.setFont(QFont('Arial', 15))
        self.output_api_label.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนสำหรับเลือกว่าจะให้เเสดงข้อมูลเกี่ยวกับอะไรของ tweet ที่เลือก
        self.label_control = QComboBox(self)
        self.label_control.addItem('time')
        self.label_control.addItem('places')
        self.label_control.move(300, 120)
        self.label_control.setFont(QFont('Arial', 13))
        self.label_control.activated.connect(lambda : self.output_control(self.output_api_label ,"tw"))
        
        # ส่วนที่บอกว่า tweet ต่างๆจะเเสดงอยู่ไหน
        self.sentence_label = QLabel('Related sentences', self)
        self.sentence_label.move(10, 160)
        self.sentence_label.setFont(QFont('Arial', 15))
        self.sentence_label.setStyleSheet("background-color : white; border : 1px solid black;")

        # ส่วนที่จะเเสดง tweet ต่างๆ
        self.sentence_show = QComboBox(self)
        self.sentence_show.activated.connect(lambda : self.sentences_support(self.tweet_dictionary ,self.sentence_show ,self.output_api_label ,"tw"))
        self.sentence_show.move(250, 160)
        self.sentence_show.resize(1200,30)
        self.sentence_show.setFont(QFont('Arial', 15))

        # ส่วนที่บอกว่า top trend tweet จะเเสดงอยู่ไหน
        self.trend_label = QLabel('trend tweet', self)
        self.trend_label.move(70, 210)
        self.trend_label.setFont(QFont('Arial', 15))
        self.trend_label.setStyleSheet("background-color : white; border : 1px solid black;")

        # ส่วนที่จะเเสดง top trend tweet
        self.trend_show =  QTextBrowser(self)
        self.trend_show.move(10, 250)
        self.trend_show.resize(260,220)
        self.trend_show.setFont(QFont('Arial', 11))
        self.trend_show.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")
        self.trend_tweet_plot()

        # ส่วนบอกจุดที่จะเเสดง word rank ของ api
        self.rank_show_label = QLabel('rank', self)
        self.rank_show_label.move(110, 490)
        self.rank_show_label.setFont(QFont('Arial', 15))
        self.rank_show_label.setStyleSheet("background-color : white; border : 1px solid black;")

        # ส่วนบอกจุดที่จะเเสดง sentiment ของ api
        self.sentiment_show_label = QLabel('sentiment', self)
        self.sentiment_show_label.move(75, 490)
        self.sentiment_show_label.setFont(QFont('Arial', 15))
        self.sentiment_show_label.setStyleSheet("background-color : white; border : 1px solid black;")
        self.sentiment_show_label.hide()

        # ส่วนจะเเสดงรายละเอียดที่อยู่ในกราฟ pie ของ api
        self.label_show =  QTextBrowser(self)
        self.label_show.move(10, 530)
        self.label_show.resize(260,220)
        self.label_show.setFont(QFont('Arial', 15))
        self.label_show.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนที่เเสดง word rank ของ api ในรูปเเบบ pie graph
        self.api_rank_show = QTextBrowser(self)
        self.api_rank_show.move(280,210)
        self.api_rank_show.resize(600,540)

        # ส่วนที่เเสดง sentiment ของ api ในรูปเเบบ pie graph
        self.api_sentiment_show = QTextBrowser(self)
        self.api_sentiment_show.move(280,210)
        self.api_sentiment_show.resize(600,540)
        self.api_sentiment_show.hide()

        # ส่วนที่เเสดงที่อยู่ต่างๆของเเต่ละ tweet ของ api ในเเผนที่
        self.api_map_show = QTextBrowser(self)
        self.api_map_show.move(890,210)
        self.api_map_show.resize(600,540)

        # ปุ่มสำหรับเลือกเเสดง word rank pie graph ของ api
        self.button_for_api_graph = QPushButton('rank', self)
        self.button_for_api_graph.resize(80,25)
        self.button_for_api_graph.move(280,210)
        self.button_for_api_graph.setFont(QFont('Times', 8)) 
        self.button_for_api_graph.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_for_api_graph.setEnabled(False)

        # ปุ่มสำหรับเลือกเเสดง sentiment pie graph ของ api
        self.button_for_api_sentiment = QPushButton('sentiment', self)
        self.button_for_api_sentiment.resize(80,25)
        self.button_for_api_sentiment.move(360,210)
        self.button_for_api_sentiment.setFont(QFont('Times', 8)) 
        self.button_for_api_sentiment.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ปุ่มสำหรับเปลี่ยน page เป็น crawler mode
        self.web_mode_button = QPushButton('crawler mode', self)
        self.web_mode_button.resize(300,60)
        self.web_mode_button.move(200,800)
        self.web_mode_button.setFont(QFont('Times', 25)) 
        self.web_mode_button.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ส่วนสำหรับปุ่มกดย้อนไป menu GUI
        self.button_back = QPushButton('back to menu', self)
        self.button_back.resize(300,60)
        self.button_back.move(600,800)
        self.button_back.setFont(QFont('Times', 25)) 
        self.button_back.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ส่วนสำหรับปุ่มกดปิด GUI
        self.button_exit = QPushButton('Exit', self)
        self.button_exit.resize(300,60)
        self.button_exit.move(1000,800)
        self.button_exit.setFont(QFont('Times', 25)) 
        self.button_exit.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        #- - - - - - - - - - - - - - - - - - - - - - - - - crawler - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # ปุ่มสำหรับเปลี่ยน page เป็น twitter mode
        self.api_mode_button = QPushButton('twiter mode', self)
        self.api_mode_button.resize(300,60)
        self.api_mode_button.move(200,800)
        self.api_mode_button.setFont(QFont('Times', 25)) 
        self.api_mode_button.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.api_mode_button.hide()

        # ส่วนหัวข้อของ web mode ของ GUI
        self.label_web_head = QLabel(' crawler GUI ', self)
        self.label_web_head.move(600, 10)
        self.label_web_head.setFont(QFont('Arial', 30))
        self.label_web_head.hide()

        # ส่วนรับ input ของ web
        self.web_input = QLineEdit(self)
        self.web_input.move(125, 80)
        self.web_input.resize(350, 30)
        self.web_input.setFont(QFont('Arial', 15))
        self.web_input.hide()

        # ปุ่มสำหรับนำ keyword เเละช่วงเวลาไปเรียกข้อมูลของ web crawler
        self.web_button = QPushButton('search', self)
        self.web_button.resize(180,30)
        self.web_button.move(970,80)
        self.web_button.setFont(QFont('Times', 15)) 
        self.web_button.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.web_button.hide()

        # ส่วน progress bar ของ web เพื่อบอกว่า code ทำ backend ของ web เสร็จหรือยัง
        self.pbar2 = QProgressBar(self)
        self.pbar2.resize(300,30)
        self.pbar2.move(1155,80)
        self.pbar2.setFont(QFont('Times', 15))
        self.pbar2.setValue(0)
        self.pbar2.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.pbar2.hide()

        # ส่วนที่ให้เลือกเวลาเริ่มต้นที่จะเเสดงข้อมูลของ web
        self.web_time_start = QDateEdit(self)
        self.web_time_start.setMaximumDate(QtCore.QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d"))))
        self.web_time_start.setGeometry(580, 80, 150, 30)
        self.web_time_start.setDate(time_defult)
        self.web_time_start.setCalendarPopup(True)
        self.web_time_start.hide()

        # ส่วนที่ให้เลือกเวลาจบที่จะเเสดงข้อมูลของ web
        self.web_time_end = QDateEdit(self)
        self.web_time_end.setMaximumDate(QtCore.QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d"))))
        self.web_time_end.setGeometry(815, 80, 150, 30)
        self.web_time_end.setDate(time_defult)
        self.web_time_end.setCalendarPopup(True)
        self.web_time_end.dateChanged.connect(lambda : self.date_limit(self.web_time_start ,self.web_time_end))
        self.web_time_end.hide()

        # ส่วนที่บอกว่าหัวข้อข่าวต่างๆจะเเสดงอยู่ไหน
        self.news_head_label = QLabel(' news head ', self)
        self.news_head_label.move(10, 120)
        self.news_head_label.setFont(QFont('Arial', 15))
        self.news_head_label.setStyleSheet("background-color : white; border : 1px solid black;")
        self.news_head_label.hide()

        # ส่วนที่จะเเสดงหัวข้อข่าวต่างๆ
        self.news_head_show = QComboBox(self)
        self.news_head_show.activated.connect(lambda : self.sentences_support(self.crawler_dictionary ,self.news_head_show ,self.output_web_label ,"web"))
        self.news_head_show.move(180, 120)
        self.news_head_show.resize(1270,30)
        self.news_head_show.setFont(QFont('Arial', 15))
        self.news_head_show.hide()

        # ส่วนที่จะเเสดงรายละเอียดต่างๆของหัวข้อข่าวนั้นๆ
        self.output_web_label =  QTextBrowser(self)
        self.output_web_label.move(140, 160)
        self.output_web_label.resize(1310,30)
        self.output_web_label.setFont(QFont('Arial', 15))
        self.output_web_label.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")
        self.output_web_label.hide()

        # ส่วนสำหรับเลือกว่าจะให้เเสดงข้อมูลเกี่ยวกับอะไรของหัวข้อข่าวที่เลือก
        self.label_control_2 = QComboBox(self)
        self.label_control_2.addItem('link')
        self.label_control_2.addItem('time')
        self.label_control_2.addItem('main link')
        self.label_control_2.move(10, 160)
        self.label_control_2.setFont(QFont('Arial', 13))
        self.label_control_2.activated.connect(lambda : self.output_control(self.output_web_label ,"web"))
        self.label_control_2.hide()

        # ส่วนบอกจุดที่จะเเสดง word rank ของ web
        self.rank_show_label_2 = QLabel('rank', self)
        self.rank_show_label_2.move(110, 210)
        self.rank_show_label_2.setFont(QFont('Arial', 15))
        self.rank_show_label_2.setStyleSheet("background-color : white; border : 1px solid black;")
        self.rank_show_label_2.hide()

        # ส่วนบอกจุดที่จะเเสดง sentiment ของ web
        self.sentiment_show_label_2 = QLabel('sentiment', self)
        self.sentiment_show_label_2.move(75, 210)
        self.sentiment_show_label_2.setFont(QFont('Arial', 15))
        self.sentiment_show_label_2.setStyleSheet("background-color : white; border : 1px solid black;")
        self.sentiment_show_label_2.hide()

        # ส่วนจะเเสดงรายละเอียดที่อยู่ในกราฟ pie ของ web
        self.label_show_2 =  QTextBrowser(self)
        self.label_show_2.move(10, 250)
        self.label_show_2.resize(260,500)
        self.label_show_2.setFont(QFont('Arial', 15))
        self.label_show_2.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")
        self.label_show_2.hide()

        # ส่วนที่เเสดง word rank ของ web ในรูปเเบบ pie graph
        self.web_rank_show = QTextBrowser(self)
        self.web_rank_show.move(280,210)
        self.web_rank_show.resize(600,540)
        self.web_rank_show.hide()

        # ส่วนที่เเสดง sentiment ของ web ในรูปเเบบ pie graph
        self.web_sentiment_show = QTextBrowser(self)
        self.web_sentiment_show.move(280,210)
        self.web_sentiment_show.resize(600,540)
        self.web_sentiment_show.hide()

        # ส่วนสำหรับเเสดงเนื้อข่าวของหัวข้อข่าวที่เลือก
        self.web_content_show = QTextBrowser(self)
        self.web_content_show.move(890,210)
        self.web_content_show.resize(600,540)
        self.web_content_show.hide()

        # ปุ่มสำหรับเลือกเเสดง word rank pie graph ของ web
        self.button_for_web_graph = QPushButton('rank', self)
        self.button_for_web_graph.resize(80,25)
        self.button_for_web_graph.move(280,210)
        self.button_for_web_graph.setFont(QFont('Times', 8)) 
        self.button_for_web_graph.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_for_web_graph.setEnabled(False)
        self.button_for_web_graph.hide()

        # ปุ่มสำหรับเลือกเเสดง sentiment pie graph ของ web
        self.button_for_web_sentiment = QPushButton('sentiment', self)
        self.button_for_web_sentiment.resize(80,25)
        self.button_for_web_sentiment.move(360,210)
        self.button_for_web_sentiment.setFont(QFont('Times', 8)) 
        self.button_for_web_sentiment.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_for_web_sentiment.hide()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.api_button.clicked.connect(self.api_search_function)
        self.button_for_api_graph.clicked.connect(self.rank_mode_function)
        self.button_for_api_sentiment.clicked.connect(self.sentiment_mode_function)
        self.web_mode_button.clicked.connect(self.crawler_mode)

        self.button_back.clicked.connect(self.back_to_menu)
        self.button_exit.clicked.connect(QApplication.instance().quit)

        self.api_mode_button.clicked.connect(self.twiter_mode)
        self.web_button.clicked.connect(self.web_search_function)
        self.button_for_web_graph.clicked.connect(self.rank_mode_function_2)
        self.button_for_web_sentiment.clicked.connect(self.sentiment_mode_function_2)


    def back_to_menu(self) :           # เป็น function ที่เชื่อมต่อ GUI นี้กับหน้า menu
        self.switch_window.emit()


    def sentence_function(self,data_file ,data_operand,element,head) :      # function สำหรับการนำข้อมูล data flame ที่ดึงออกมาจาก database เเล้วมาเก็บในตัวเเปรของ class
        for column in data_file :
            data_operand[column] = []
        for column in data_file :
            for inner in data_file[column] :
                data_operand[column].append(inner)

        for word in data_operand[head] :
            element.addItem(word)

    def sentences_support(self,data_operand ,element ,target ,mode) :       # function สำหรับการรับข้อมูลจาก collumn ใด collumn หนึ่งเเละจะนำ index ของข้อมูลใน collumn นั้นเพื่อที่จะนำไปหาข้อมูลใน collumn อื่นๆ
        data = element.currentText()
        key_mark = self.find_keys_by_values(data ,data_operand)
        tem_index = int()
        try :
            for index in range(len(data_operand[key_mark])) :
                if data_operand[key_mark][index] == data :
                    tem_index = index
            new_data = data_operand
            if mode == "tw" :
                self.api_result = []
                for token,key in zip(new_data.values(),new_data.keys()) :
                    if key != key_mark :
                        self.api_result.append(token[tem_index])
        
                self.output_control(target ,mode)

            elif mode == "web" :
                self.web_result = []
                for token,key in zip(new_data.values(),new_data.keys()) :
                    if key != key_mark :
                        self.web_result.append(token[tem_index])

                self.web_content_show.clear()
                self.web_content_show.append(str(self.web_result[1]))
                self.output_control(target ,mode)
        except KeyError :
            pass


    def find_keys_by_values(self,values ,data_operand) :           # function สำหรับการช่วยหาชื่อ collumn จากข้อมูลใน collumn เป้าหมาย
        test = data_operand.items()
        for item in test :
            if values in item[1] :
                return item[0]
                break
            else :
                pass

    def output_control(self,target ,mode) :          # function สำหรับการควบคุมข้อมูลที่จะใส่ลงไปในตัวเเปรที่ต้องการ
        try :
            if mode == "tw" :             # ทำเมื่ออยู่ใน crawler page
                if self.label_control.currentText() == 'time' :
                    target.clear()
                    target.append(str(self.api_result[1]))
                elif self.label_control.currentText() == 'places' :
                    target.clear()
                    target.append(str(self.api_result[0]))
            elif mode == "web" :          # ทำเมื่ออยู่ใน twitter page
                if self.label_control_2.currentText() == 'link' :
                    target.clear()
                    target.append(str(self.web_result[0]))
                elif self.label_control_2.currentText() == 'time' :
                    target.clear()
                    target.append(str(self.web_result[2]))
                elif self.label_control_2.currentText() == 'main link' :
                    target.clear()
                    target.append(str(self.web_result[3]))
        except IndexError :
                target.clear()


    def rank_mode_function(self) :           # function สำหรับการเเสดงเฉพาะกราฟ rank ของ twitter
        self.api_rank_state = True
        self.api_sentiment_state = False

        self.button_for_api_graph.setEnabled(False)
        self.button_for_api_sentiment.setEnabled(True)
        self.api_rank_show.show()
        self.api_sentiment_show.hide()

        self.rank_show_label.show()
        self.sentiment_show_label.hide()

        self.label_show.clear()
        try :
            self.rank_label_plot(self.label_show ,self.rank_file)
        except AttributeError :
            pass

    def sentiment_mode_function(self) :         # function สำหรับการเเสดงเฉพาะกราฟ sentiment ของ twitter
        self.api_sentiment_state = True
        self.api_rank_state = False

        self.button_for_api_sentiment.setEnabled(False)
        self.button_for_api_graph.setEnabled(True)
        self.api_sentiment_show.show()
        self.api_rank_show.hide()

        self.sentiment_show_label.show()
        self.rank_show_label.hide()

        self.label_show.clear()
        try :
            self.sentiment_label_plot(self.label_show ,self.result_func)
        except AttributeError :
            pass

    def rank_mode_function_2(self) :          # function สำหรับการเเสดงเฉพาะกราฟ rank ของ crawler
        self.web_rank_state = True
        self.web_sentiment_state = False

        self.button_for_web_graph.setEnabled(False)
        self.button_for_web_sentiment.setEnabled(True)
        self.web_rank_show.show()
        self.web_sentiment_show.hide()

        self.rank_show_label_2.show()
        self.sentiment_show_label_2.hide()

        self.label_show_2.clear()
        try :
            self.rank_label_plot(self.label_show_2 ,self.rank_file_2)
        except AttributeError :
            pass

    def sentiment_mode_function_2(self) :        # function สำหรับการเเสดงเฉพาะกราฟ sentiment ของ crawler
        self.web_sentiment_state = True
        self.web_rank_state = False

        self.button_for_web_sentiment.setEnabled(False)
        self.button_for_web_graph.setEnabled(True)
        self.web_sentiment_show.show()
        self.web_rank_show.hide()

        self.sentiment_show_label_2.show()
        self.rank_show_label_2.hide()

        self.label_show_2.clear()
        try :
            self.sentiment_label_plot(self.label_show_2 ,self.op_sentiment)
        except AttributeError :
            pass
        
    def date_limit(self,start_element ,end_element) :  # function สำหรับการกำหนดขอบเขตของ lable เวลาเริ่มไม่ให้เลือกได้เกินเวลาจบ
        get_time = end_element.date().toPyDate()
        start_element.setMaximumDate(QtCore.QDate(get_time.year, get_time.month, get_time.day))

    def format_time(self ,start ,end) :   # function สำหรับการนำเวลาที่ได้มาจาก lable เวลามาเเปลงเป็นรูป string
        data_time_1 = start
        data_time_2 = end

        day_1 ,day_2 = str(data_time_1.day) ,str(data_time_2.day)
        month_1 ,month_2 = str(data_time_1.month) ,str(data_time_2.month)
        year_1 ,year_2 = str(data_time_1.year) ,str(data_time_2.year)

        if len(day_1) == 1 or len(day_2) == 1 :
            if len(day_1) == 1 :
                day_1 = '0' + day_1
            if len(day_2) == 1 :
                day_2 = '0' + day_2
        if len(month_1) == 1 or len(month_2) == 1 :
            if len(month_1) == 1 :
                month_1 = '0' + month_1
            if len(month_2) == 1 :
                month_2 = '0' + month_2

        self.since = f'{year_1}-{month_1}-{day_1}'
        self.until = f'{year_2}-{month_2}-{day_2}'

        return (self.since,self.until)


    def trend_tweet_plot(self) :      # function สำหรับการ plot ข้อมูลของ top trend tweet ลงใน GUI 
        data = pandas.read_csv('top_trends_tweet.csv').sort_values(by = "tweet_number" ,ascending = False)

        self.trend_show.clear()
        count = 1
        for trend,number in zip(data['trends'], data['tweet_number']) :
            self.trend_show.append(f'{count}.) ' + str(trend) + '\n' + 'tweet : ' + str(number) + '\n' + '______________________' + '\n')
            count += 1


    def plot_graph_function(self,element,data,name) :    # function สำหรับการ plot graph เเบบกราฟวงกลมของ rank graph
        pie_series = QPieSeries()
        chart = QChart()

        count = 0
        count_limit = 10
        pie_series.clear()
        for key,value in zip(data['word'] ,data['number']) :
            if count < count_limit :
                pie_series.append(key ,value)
                count += 1
            else :
                break

        chart.addSeries(pie_series)
        chart.legend().setFont(QFont('Arial', 20))
        chart.setTitle(("The most words rank have used of {}").format(name))
        pie_series.setLabelsVisible()
        pie_series.setLabelsPosition(QtChart.QPieSlice.LabelInsideHorizontal)

        for slice in pie_series.slices():
            slice.setPen(QPen(Qt.darkGreen, 2))
        chartview = QChartView(chart)
        chartview.setGeometry(0,0,900,900)
        chartview.setRenderHint(QPainter.Antialiasing)

        pixmap = QPixmap(chartview.grab())
        pixmap.save(("{}_graph.png").format(name),"PNG")
        element.clear()
        element.setStyleSheet(("border-image:url({}_graph.png);").format(name))

    def sentiment_graph(self,element,data,name) :      # function สำหรับการ plot graph เเบบกราฟวงกลมของ sentiment graph
        
        positive = data[0]
        neutral = data[1]
        negative = data[2]

        pi_series = QPieSeries()
        chart = QChart()

        pi_series.append('positive' ,positive)
        pi_series.append('neutral' ,neutral)
        pi_series.append('negative' ,negative)

        chart.addSeries(pi_series)
        chart.legend().setFont(QFont('Arial', 20))
        chart.setTitle("sentiment")
        pi_series.setLabelsVisible()
        pi_series.setLabelsPosition(QtChart.QPieSlice.LabelInsideHorizontal)

        for slice in pi_series.slices():
            slice.setPen(QPen(Qt.darkGreen, 2))
        chartview = QChartView(chart)
        chartview.setGeometry(0,0,900,900)
        chartview.setRenderHint(QPainter.Antialiasing)

        pixmap = QPixmap(chartview.grab())
        pixmap.save(("{}_graph.png").format(name),"PNG")
        element.setStyleSheet(("border-image:url({}_graph.png);").format(name))


    def rank_label_plot(self,element ,data_flame) :      # function สำหรับการเเสดง rank 10 อันดับเเรกจากประโยคทั้งหมด
        count = 1
        count_limit = 10
        for word,number in zip(data_flame['word'] ,data_flame['number']) :
            if count <= count_limit :
                number_use = str(number)
                element.append(('{}.) ' + str(word) +"\n" + 'number : ' + number_use).format(count))
                count += 1
            else :
                break

    def sentiment_label_plot(self,element ,sen_list) :       # function สำหรับการเเสดงลักษณะของ sentiment ต่างๆว่าเเต่ละอย่างมีเท่าไหร่บ้างใน GUI
        temp_head = ["positive" ,"neutral" ,"negative"]
        for name ,number in zip(temp_head ,sen_list) :
            number_use = str(number)
            element.append(name + " : " + number_use + "\n")

    def api_search_function(self) :        # เป็น thread function สำหรับการทำ backend ในส่วนของ web ในขณะที่ GUI ยังตอบสนองได้อยู่

        self.tweet_dictionary = {}
        keyword = self.api_input.text()        # keyword
        usable_time = self.format_time(self.api_time_start.date().toPyDate() ,self.api_time_end.date().toPyDate())   # ช่วงเวลา

        self.pbar.setValue(5) #

        if [keyword, usable_time[0], usable_time[1]] != self.time_and_keyword :       # กรณีที่กด search โดยใช้ keyword หรือช่วงเวลาใหม่

            self.time_and_keyword = [keyword, usable_time[0], usable_time[1]]

            # เลือก function ที่จะทำ thread
            self.thread = QThread()
            self.api_thread_class = Api_thread(keyword ,usable_time)
            self.api_thread_class.moveToThread(self.thread)

            self.pbar.setValue(10) #

            # เงื่อนไขการเริ่มหรือจบ thread เเละเป็นตัวบอกว่าเมื่อจบ thread เเล้วทำอะไรต่อ
            self.thread.started.connect(self.api_thread_class.run)
            self.api_thread_class.finished.connect(self.thread.quit)
            self.api_thread_class.finished.connect(self.api_thread_class.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.api_thread_class.plot_switch.connect(self.api_plot_function)

            self.thread.start()
            self.api_button.setEnabled(False)
            self.thread.finished.connect(lambda : self.api_button.setEnabled(True))       # อนุญาติให้กด search ใหม่ได้เพราะ plot ข้อมูลเสร็จเเล้ว

        else :                                                                  # กรณีที่กด search โดยใช้ keyword เเละช่วงเวลาของครั้งที่เเล้ว
            # โหลดข้อมูลทั้งหมดของครั้งที่เเล้วเเล้วตอบเลย
            data_file = pandas.read_csv(str(keyword) + '_api.csv')
            con_1 = data_file['time'] >= f'{usable_time[0]} 00:00:00'
            con_2 = data_file['time'] <= f'{usable_time[1]} 23:59:59'
            complete_file = data_file[con_1 & con_2]

            temp_list = []
            api_sentiment = pandas.read_csv('temp_file.csv')
            for i in api_sentiment['sentiment'] :
                temp_list.append(int(i))

            self.api_plot_function(complete_file, temp_list)
        

    def api_plot_function(self,twit_frame ,api_sentiment) :

        self.pbar.setValue(50) #
        # ส่วนของการบรรทึกข้อมูล tweet ต่างๆลงใน GUI
        self.sentence_function(twit_frame ,self.tweet_dictionary ,self.sentence_show ,"tweet")
        self.sentences_support(self.tweet_dictionary ,self.sentence_show ,self.output_api_label ,"tw")

        self.pbar.setValue(60) #

        # ส่วนการ plot ข้อมูล word rank เเบบเป็น pie graph ของ api ลงใน GUI
        self.rank_file = pandas.read_csv(str(self.api_input.text()) + '_NLP.csv')
        self.plot_graph_function(self.api_rank_show ,self.rank_file ,'api_rank')

        self.pbar.setValue(70) #
        
        # ส่วนของการ plot ข้อมูล sentiment เเบบ pie graph ของ api ลงใน GUI
        self.api_sentiment_show.clear()
        self.result_func = api_sentiment
        self.sentiment_graph(self.api_sentiment_show ,self.result_func ,"twitter_sentiment")

        self.pbar.setValue(80) #

        self.api_map_show.clear()
        self.api_map_show.setStyleSheet(("border-image:url(coordinates_file.png);"))

        if self.button_for_api_graph.isEnabled()  == False :
            self.label_show.clear()
            self.rank_label_plot(self.label_show ,self.rank_file)      # ส่วนการ plot ข้อมูล word rank ของ api ลงใน GUI
        elif self.button_for_api_graph.isEnabled() == True:
            self.label_show.clear()
            self.sentiment_label_plot(self.label_show ,self.result_func)        # ส่วนการ plot ข้อมูล sentiment ของ api ลงใน GUI

        self.pbar.setValue(100) #
        t.sleep(0.75)
        self.pbar.setValue(0) #

    def web_search_function(self) :

        self.crawler_dictionary = {}
        keyword = self.web_input.text()           # keyword
        usable_time = self.format_time(self.web_time_start.date().toPyDate() ,self.web_time_end.date().toPyDate())     # ช่วงเวลา

        self.pbar2.setValue(5) #

        # เลือก function ที่จะทำ thread
        self.thread2 = QThread()
        self.web_thread_class = Web_thread(keyword ,usable_time)
        self.web_thread_class.moveToThread(self.thread2)

        self.pbar2.setValue(10) #

        # เงื่อนไขการเริ่มหรือจบ thread เเละเป็นตัวบอกว่าเมื่อจบ thread เเล้วทำอะไรต่อ
        self.thread2.started.connect(self.web_thread_class.run)
        self.web_thread_class.finished.connect(self.thread2.quit)
        self.web_thread_class.finished.connect(self.web_thread_class.deleteLater)
        self.thread2.finished.connect(self.thread2.deleteLater)
        self.web_thread_class.plot_switch.connect(self.web_plot_function)

        self.thread2.start()
        self.web_button.setEnabled(False)
        self.thread2.finished.connect(lambda : self.web_button.setEnabled(True))      # อนุญาติให้กด search ใหม่ได้เพราะ plot ข้อมูลเสร็จเเล้ว


    def web_plot_function(self,web_sentiment ,crawler_dictionary) :

        self.pbar2.setValue(50) #

        self.op_sentiment ,self.crawler_dictionary = web_sentiment ,crawler_dictionary

        # ส่วนของการบรรทึกข้อมูลข่าวต่างๆลงใน GUI
        for word in self.crawler_dictionary["head_news"] :
            self.news_head_show.addItem(word)

        self.pbar2.setValue(60) #

        if len(self.crawler_dictionary['head_news']) == 0 :
            pass
        else :
            self.sentences_support(self.crawler_dictionary ,self.news_head_show ,self.output_web_label ,"web")

        self.pbar2.setValue(70) #

        # ส่วนการ plot ข้อมูล word rank เเบบเป็น pie graph ของ web ลงใน GUI
        self.rank_file_2 = pandas.read_csv('Web_crawler_NLP_4.csv')
        self.plot_graph_function(self.web_rank_show ,self.rank_file_2 ,'webside_rank')

        self.pbar2.setValue(80) #
        
        # ส่วนของการ plot ข้อมูล sentiment เเบบ pie graph ของ web ลงใน GUI
        self.web_sentiment_show.clear()
        self.sentiment_graph(self.web_sentiment_show ,self.op_sentiment ,"webside_sentiment")

        self.pbar2.setValue(90) #

        if self.button_for_web_graph.isEnabled()  == False :
            self.label_show_2.clear()
            self.rank_label_plot(self.label_show_2 ,self.rank_file_2)      # ส่วนการ plot ข้อมูล word rank ของ web ลงใน GUI
        elif self.button_for_web_graph.isEnabled() == True:
            self.label_show_2.clear()
            self.sentiment_label_plot(self.label_show_2 ,self.op_sentiment)      # ส่วนการ plot ข้อมูล sentiment ของ web ลงใน GUI

        self.pbar2.setValue(100) #
        t.sleep(0.75)
        self.pbar2.setValue(0) #


    def crawler_mode(self) :            # function สำหรับเเสดง crawler GUI
        self.label_api_head.hide()
        self.api_input.hide()
        self.api_button.hide()
        self.pbar.hide()
        self.api_time_end.hide()
        self.api_time_start.hide()
        self.output_api_label.hide()
        self.label_control.hide()
        self.sentence_label.hide()
        self.sentence_show.hide()
        self.trend_label.hide()
        self.trend_show.hide()
        self.rank_show_label.hide()
        self.sentiment_show_label.hide()
        self.label_show.hide()
        self.api_rank_show.hide()
        self.api_sentiment_show.hide()
        self.api_map_show.hide()
        self.button_for_api_graph.hide()
        self.button_for_api_sentiment.hide()
        self.web_mode_button.hide()

        self.api_mode_button.show()
        self.label_web_head.show()
        self.web_input.show()
        self.web_button.show()
        self.pbar2.show()
        self.web_time_start.show()
        self.web_time_end.show()
        self.news_head_label.show()
        self.news_head_show.show()
        self.output_web_label.show()
        self.label_control_2.show()
        self.label_show_2.show()
        self.web_content_show.show()
        self.button_for_web_graph.show()
        self.button_for_web_sentiment.show()
        if (self.web_rank_state == True) and (self.web_sentiment_state == False) :
            self.rank_show_label_2.show()
            self.sentiment_show_label_2.hide()
            self.web_rank_show.show()
            self.web_sentiment_show.hide()
        elif (self.web_rank_state == False) and (self.web_sentiment_state == True) :
            self.rank_show_label_2.hide()
            self.sentiment_show_label_2.show()
            self.web_rank_show.hide()
            self.web_sentiment_show.show()

    def twiter_mode(self) :            # function สำหรับเเสดง twitter api GUI
        self.api_mode_button.hide()
        self.label_web_head.hide()
        self.web_input.hide()
        self.web_button.hide()
        self.pbar2.hide()
        self.web_time_start.hide()
        self.web_time_end.hide()
        self.news_head_label.hide()
        self.news_head_show.hide()
        self.output_web_label.hide()
        self.label_control_2.hide()
        self.rank_show_label_2.hide()
        self.sentiment_show_label_2.hide()
        self.label_show_2.hide()
        self.web_rank_show.hide()
        self.web_sentiment_show.hide()
        self.web_content_show.hide()
        self.button_for_web_graph.hide()
        self.button_for_web_sentiment.hide()

        self.label_api_head.show()
        self.api_input.show()
        self.api_button.show()
        self.pbar.show()
        self.api_time_end.show()
        self.api_time_start.show()
        self.output_api_label.show()
        self.label_control.show()
        self.sentence_label.show()
        self.sentence_show.show()
        self.trend_label.show()
        self.trend_show.show()
        self.label_show.show()
        self.api_map_show.show()
        self.web_mode_button.show()
        self.button_for_api_graph.show()
        self.button_for_api_sentiment.show()
        if (self.api_rank_state == True) and (self.api_sentiment_state == False) :
            self.rank_show_label.show()
            self.sentiment_show_label.hide()
            self.api_rank_show.show()
            self.api_sentiment_show.hide()
        elif (self.api_rank_state == False) and (self.api_sentiment_state == True) :
            self.rank_show_label.hide()
            self.sentiment_show_label.show()
            self.api_rank_show.hide()
            self.api_sentiment_show.show()


#___________________________________________________________________________________________________________________________________________

class Web_thread(QObject) :        # class สำหรับทำในส่วนของ backend ทั้งหมดที่จำเป็นในการเเสดงข้อมูลของ GUI ใน web mode
    finished = pyqtSignal()
    plot_switch = pyqtSignal(list ,dict)
    def __init__(self,keyword, usable_time) :        # ส่วนสำหรับ set ค่า input ที่ได้รับมา
        super().__init__()
        self.keyword = keyword
        self.usable_time = usable_time
    def run(self) :                # ส่วนสำหรับเริ่มทำงาน
        keyword = self.keyword
        usable_time = self.usable_time

        #- - - - - - - - - - - - - - - - - - -
        now = datetime.now()
        
        # ส่วนสำหรับการดึงข้อมูลของ web จาก database ที่ต้องการเเละทำการตัดคำหา word rank เเละ sentiment ให้ด้วย
        op_sentiment ,crawler_dictionary = search_and_sentiment(keyword ,usable_time[0] ,usable_time[1])
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        finish = datetime.now()
        print("time use : ",finish - now)

        # เป็นส่วนบอกว่าได้ข้อมูลครบเเล้วให้จบ thread ได้เลยเเละนำข้อมูลไปให้ GUI
        self.plot_switch.emit(op_sentiment ,crawler_dictionary)
        self.finished.emit()

#___________________________________________________________________________________________________________________________________________

class Api_thread(QObject) :        # class สำหรับทำในส่วนของ backend ทั้งหมดที่จำเป็นในการเเสดงข้อมูลของ GUI ใน api mode
    finished = pyqtSignal()
    plot_switch = pyqtSignal(pandas.core.frame.DataFrame ,list)
    def __init__(self,keyword, usable_time) :           # ส่วนสำหรับ set ค่า input ที่ได้รับมา
        super().__init__()
        self.keyword = keyword
        self.usable_time = usable_time
    def run(self) :                # ส่วนสำหรับเริ่มทำงาน
        keyword = self.keyword
        usable_time = self.usable_time

        #- - - - - - - - - - - - - - - - - - -
        now = datetime.now()
        
        # ส่วนสำหรับตรวจสอบว่าข้อมูลของ api จาก database ที่ต้องการว่ามีข้อมูลครบทุกวันตามช่วงเวลาที่ต้องการหรือไม่ถ้าไม่ให้ update database
        api_view(keyword ,usable_time[0] ,usable_time[1])

        # ส่วนสำหรับดึงข้อมูลของ api จาก database ที่ต้องการตามช่วงเวลาที่ต้องการหลังจาก update database เเล้ว
        data_file = pandas.read_csv(str(keyword) + '_api.csv')
        con_1 = data_file['time'] >= f'{usable_time[0]} 00:00:00'
        con_2 = data_file['time'] <= f'{usable_time[1]} 23:59:59'
        complete_file = data_file[con_1 & con_2]

        # ส่วนสำหรับนำข้อมูลที่ได้มาหาพิกัดในเเผนที่โลกของเเต่ละ tweet
        thread_1 = Thread(target = coordinate_ploter , args = [complete_file])
        thread_1.start()

        # ส่วนสำหรับนำข้อมูลที่ได้มาตัดคำหา word rank ของ api
        NLP(str(keyword) ,complete_file)
        
        # ส่วนสำหรับนำข้อมูลที่ได้มาหา sentiment ของ api
        func = sentiment()
        result_func = func.sentiment_englist(complete_file ,"tweet")

        thread_1.join()
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        finish = datetime.now()
        print("time use : ",finish - now)

        # เป็นส่วนบอกว่าได้ข้อมูลครบเเล้วให้จบ thread ได้เลยเเละนำข้อมูลไปให้ GUI
        self.plot_switch.emit(complete_file , result_func)
        self.finished.emit()


#_________________________________________________________________________________________________________________________________________________________

def coordinate_ploter(data_frame) :        # function สำหรับ map
    geopy2(data_frame)
    plotly()

#_________________________________________________________________________________________________________________________________________________________



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    web = Api_and_crawler_GUI()
    web.show()
    sys.exit(app.exec_())

