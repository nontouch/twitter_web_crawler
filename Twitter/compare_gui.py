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

from threading import *
import queue as Queue

from twiter_api import *
from crawler import *
from main_menu_gui import *

class Compare(QWidget) :        # class GUI สำหรับการ compare ระหว่าง twiter เเละ crawler เเละ stock GUI
    switch_window = QtCore.pyqtSignal()
    def __init__(self):                # ส่วนสำหรับการตั้งค่าหน้าต่าง GUI

        super().__init__()
        self.title = 'compare gui'
        self.image = 'temp_bg.jpg'
        self.icon = "Shrimp-front.png"
        self.left = 300 
        self.top = 100
        self.width = 1500
        self.height = 900
        self.palette = QPalette()
        self.vbox = QVBoxLayout()

        self.compare_thread = True

        self.initUI()

    def initUI(self) :                 # ส่วนสำหรับการวาง element ต่างๆในหน้าต่าง GUI
        # ส่วนสำหรับตั้งชื่อ title เเละ set ขนาดของ GUI
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # ส่วนสำหรับวาง background ของ GUI
        background = QImage(self.image)
        background_side = background.scaled(QSize(self.width,self.height))  
        self.palette.setBrush(QPalette.Window, QBrush(background_side))
        self.setPalette(self.palette)

        # ส่วนสำหรับปุ่มกดย้อนไป menu GUI
        self.button_out = QPushButton('back', self)
        self.button_out.resize(200,40)
        self.button_out.move(520,850)
        self.button_out.setFont(QFont('Times', 20)) 
        self.button_out.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_out.setIcon(QIcon(self.icon))

        # ส่วนสำหรับปุ่มกดปิด GUI
        self.button_exit = QPushButton('Exit', self)
        self.button_exit.resize(200,40)
        self.button_exit.move(780,850)
        self.button_exit.setFont(QFont('Times', 20)) 
        self.button_exit.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_exit.setIcon(QIcon(self.icon))

        # ส่วนหัวข้อของ GUI
        self.label_head = QLabel('Stock and compare between twiter and webside', self)
        self.label_head.move(200, 10)
        self.label_head.setFont(QFont('Arial', 30))

        #- - - - - - - - - - - - - ส่วน stock - - - - - - - - - - - - - - - - -

        # ส่วนบอกจุดที่ต้องใส่ input ของ stock
        self.label_stock = QLabel('Stock :', self)
        self.label_stock.move(10, 70)
        self.label_stock.setFont(QFont('Arial', 15))

        # ส่วนรับ input ของ stock
        self.stock_input = QLineEdit(self)
        self.stock_input.move(95, 70)
        self.stock_input.resize(350, 30)
        self.stock_input.setFont(QFont('Arial', 15))

        # ปุ่ม search สำหรับนำ keyword เเละช่วงเวลาของ stock ไปเรียกข้อมูลของหุ้น
        self.stock_button = QPushButton('search', self)
        self.stock_button.resize(180,30)
        self.stock_button.move(450,70)
        self.stock_button.setFont(QFont('Times', 15)) 
        self.stock_button.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ส่วนเเสดงกราฟหุ้นประเภทเส้น
        self.stock_graph =  QTextBrowser(self)
        self.stock_graph.move(10,110)
        self.stock_graph.resize(440,325)
        self.stock_graph.setFont(QFont('Arial', 15))
        self.stock_graph.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนเเสดงกราฟหุ้นประเภทเทียน
        self.stock_graph_2 =  QTextBrowser(self)
        self.stock_graph_2.move(10,110)
        self.stock_graph_2.resize(440,325)
        self.stock_graph_2.setFont(QFont('Arial', 15))
        self.stock_graph_2.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")
        self.stock_graph_2.hide()

        # ปุ่มสำหรับเลือกเเสดงกราฟเส้น
        self.stock_line = QPushButton('line', self)
        self.stock_line.resize(60,20)
        self.stock_line.move(10,110)
        self.stock_line.setFont(QFont('Times', 10)) 
        self.stock_line.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.stock_line.setEnabled(False)

        # ปุ่มสำหรับเลือกเเสดงกราฟเทียน
        self.stock_candle = QPushButton('Candlestick', self)
        self.stock_candle.resize(100,20)
        self.stock_candle.move(70,110)
        self.stock_candle.setFont(QFont('Times', 10)) 
        self.stock_candle.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ส่วนที่บอกว่าเวลาเริ่มต้นอยู่ไหน
        self.start_time = QLabel('start time :', self)
        self.start_time.move(460, 110)
        self.start_time.setFont(QFont('Arial', 15))

        # ส่วนที่บอกว่าเวลาจบอยู่ไหน
        self.end_time = QLabel('end time :', self)
        self.end_time.move(460, 250)
        self.end_time.setFont(QFont('Arial', 15))

        # ส่วนที่ให้เลือกเวลาจบที่จะเเสดงข้อมูล
        self.time_label_all_2 = QDateEdit(self)
        self.time_label_all_2.setMaximumDate(QtCore.QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d"))))
        self.time_label_all_2.setGeometry(460, 300, 150, 40)
        defult_2 = QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d")))
        self.time_label_all_2.setDate(defult_2)
        self.time_label_all_2.setCalendarPopup(True)
        self.time_label_all_2.dateChanged.connect(self.date_limit)

        # ส่วนที่ให้เลือกเวลาเริ่มต้นที่จะเเสดงข้อมูล
        self.time_label_all_1 = QDateEdit(self)
        self.time_label_all_1.setMaximumDate(QtCore.QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d"))))
        self.time_label_all_1.setGeometry(460, 160, 150, 40)
        defult_1 = QDate(int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d")))
        self.time_label_all_1.setDate(defult_1)
        self.time_label_all_1.setCalendarPopup(True)

        #- - - - - - - - - - - - - ส่วน compare - - - - - - - - - - - - - - - - -

        # ส่วนบอกจุดที่ต้องใส่ input ของ compare
        self.label_compare = QLabel('twiter and web :', self)
        self.label_compare.move(760, 70)
        self.label_compare.setFont(QFont('Arial', 15))

        # ส่วนรับ input ของ compare
        self.compare_input = QLineEdit(self)
        self.compare_input.move(945, 70)
        self.compare_input.resize(350, 30)
        self.compare_input.setFont(QFont('Arial', 15))

        # ปุ่มสำหรับนำ keyword เเละช่วงเวลาไปเรียกข้อมูลของ twit เเละ web
        self.compare_button = QPushButton('compare', self)
        self.compare_button.resize(180,30)
        self.compare_button.move(1300,70)
        self.compare_button.setFont(QFont('Times', 15)) 
        self.compare_button.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")

        # ส่วนบอกจุดที่จะเเสดง word rank ของ api
        self.api_rank_label = QLabel('twiter word rank', self)
        self.api_rank_label.move(770, 110)
        self.api_rank_label.setFont(QFont('Arial', 12.5))
        self.api_rank_label.setStyleSheet("background-color : white; border : 1px solid black;")

        # ส่วนบอกจุดที่จะเเสดง sentiment ของ api
        self.api_sentiment_label = QLabel('twiter sentiment', self)
        self.api_sentiment_label.move(960, 110)
        self.api_sentiment_label.setFont(QFont('Arial', 12.5))
        self.api_sentiment_label.setStyleSheet("background-color : white; border : 1px solid black;")

        # ส่วนบอกจุดที่จะเเสดง word rank ของ web
        self.web_rank_label = QLabel('web word rank', self)
        self.web_rank_label.move(1150, 110)
        self.web_rank_label.setFont(QFont('Arial', 12.5))
        self.web_rank_label.setStyleSheet("background-color : white; border : 1px solid black;")

        # ส่วนบอกจุดที่จะเเสดง sentiment ของ web
        self.web_sentiment_label = QLabel('web sentiment', self)
        self.web_sentiment_label.move(1335, 110)
        self.web_sentiment_label.setFont(QFont('Arial', 12.5))
        self.web_sentiment_label.setStyleSheet("background-color : white; border : 1px solid black;")

        # ส่วนที่เเสดง word rank ของ api
        self.api_rank_show =  QTextBrowser(self)
        self.api_rank_show.move(760,150)
        self.api_rank_show.resize(175,285)
        self.api_rank_show.setFont(QFont('Arial', 12.5))
        self.api_rank_show.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนที่เเสดง sentiment ของ api
        self.api_sentiment_show =  QTextBrowser(self)
        self.api_sentiment_show.move(945,150)
        self.api_sentiment_show.resize(175,285)
        self.api_sentiment_show.setFont(QFont('Arial', 15))
        self.api_sentiment_show.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนที่เเสดง word rank ของ web
        self.web_rank_show =  QTextBrowser(self)
        self.web_rank_show.move(1130,150)
        self.web_rank_show.resize(175,285)
        self.web_rank_show.setFont(QFont('Arial', 12.5))
        self.web_rank_show.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนที่เเสดง sentiment ของ web
        self.web_sentiment_show =  QTextBrowser(self)
        self.web_sentiment_show.move(1315,150)
        self.web_sentiment_show.resize(175,285)
        self.web_sentiment_show.setFont(QFont('Arial', 15))
        self.web_sentiment_show.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")


        # ส่วนที่เเสดง word rank ของ api ในรูปเเบบ pie graph
        self.api_rank_graph =  QTextBrowser(self)
        self.api_rank_graph.move(10,450)
        self.api_rank_graph.resize(365,325)
        self.api_rank_graph.setFont(QFont('Arial', 15))
        self.api_rank_graph.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนที่เเสดง sentiment ของ api ในรูปเเบบ pie graph
        self.api_sentiment_graph =  QTextBrowser(self)
        self.api_sentiment_graph.move(380,450)
        self.api_sentiment_graph.resize(365,325)
        self.api_sentiment_graph.setFont(QFont('Arial', 15))
        self.api_sentiment_graph.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนที่เเสดง word rank ของ web ในรูปเเบบ pie graph
        self.web_rank_graph =  QTextBrowser(self)
        self.web_rank_graph.move(755,450)
        self.web_rank_graph.resize(365,325)
        self.web_rank_graph.setFont(QFont('Arial', 15))
        self.web_rank_graph.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        # ส่วนที่เเสดง sentiment ของ web ในรูปเเบบ pie graph
        self.web_sentiment_graph =  QTextBrowser(self)
        self.web_sentiment_graph.move(1125,450)
        self.web_sentiment_graph.resize(365,325)
        self.web_sentiment_graph.setFont(QFont('Arial', 15))
        self.web_sentiment_graph.setStyleSheet("QLineEdit" "{" "background-color : lightblue;" "}")

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.stock_button.clicked.connect(self.button_for_stock)           # connect line 323
        self.stock_line.clicked.connect(self.button_mode_line)             # connect line 330
        self.stock_candle.clicked.connect(self.button_mode_candle)         # connect line 336

        self.compare_button.clicked.connect(self.button_for_compare)       # connect line 516
        
        self.button_out.clicked.connect(self.back_to_menu)                 # connect line 291
        self.button_exit.clicked.connect(QApplication.instance().quit)     # สั่งให้ปิด GUI ทั้งหมด

        
    def back_to_menu(self) :    # เป็น function ที่เชื่อมต่อ GUI นี้กับหน้า menu
        self.switch_window.emit()


    def date_limit(self) :  # function สำหรับการกำหนดขอบเขตของ lable เวลาเริ่มไม่ให้เลือกได้เกินเวลาจบ
        get_time = self.time_label_all_2.date().toPyDate()
        self.time_label_all_1.setMaximumDate(QtCore.QDate(get_time.year, get_time.month, get_time.day))

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

    def button_for_stock(self) : # function สำหรับการนำ keyword ในส่วนของ stock มาทำ stock เเละ plot graph
        time_usable = self.format_time(self.time_label_all_1.date().toPyDate() ,self.time_label_all_2.date().toPyDate())  # format เวลาที่รับมาจาก GUI เเปลงเป็น string
        crawler_stock(self.stock_input.text() ,time_usable[0] ,time_usable[1])   # นำ input ทั้งหมดไปหาข้อมูลหุ้น
        #- - - - ส่วนวาดกราฟ - - - -
        self.plot_graph(self.stock_graph)   # line graph function
        self.plot_graph_2(self.stock_graph_2)     # candle graph function

    def button_mode_line(self) :      # function สำหรับการเลือกเเสดง graph เเบบกราฟเส้นของ stock graph
        self.stock_line.setEnabled(False)
        self.stock_candle.setEnabled(True)
        self.stock_graph_2.hide()
        self.stock_graph.show()

    def button_mode_candle(self) :       # function สำหรับการเลือกเเสดง graph เเบบกราฟเเทงของ stock graph
        self.stock_candle.setEnabled(False)
        self.stock_line.setEnabled(True)
        self.stock_graph.hide()
        self.stock_graph_2.show()

    def plot_graph(self,element) :   # function สำหรับการ plot graph เเบบกราฟเส้นของ stock graph
        output_file = pandas.read_csv("crawler_stock.csv")
        plt.xlabel('Date')
        plt.ylabel('Close price')
        plt.figure(figsize = (6,4))
        plt.plot(output_file["Date"],output_file["Adj Close"],"b--")
        plt.savefig("stock_crawler_graph.png")

        element.clear()
        element.setStyleSheet("border-image:url(stock_crawler_graph.png);")

    def plot_graph_2(self,element) :         # function สำหรับการ plot graph เเบบกราฟเเทงของ stock graph
        try :
            output_file = pandas.read_csv("crawler_stock.csv")
            #print(output_file)
            plt.style.use('ggplot')
            ohlc = output_file.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
            ohlc['Date'] = pandas.to_datetime(ohlc['Date'])
            ohlc['Date'] = ohlc['Date'].apply(plt_date.date2num)
            ohlc = ohlc.astype(float)

            # Creating Subplots
            fig, ax = plt.subplots()
            print(fig, ax)

            candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)

            # Setting labels & titles
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            fig.suptitle('Daily Candlestick Chart of NIFTY50')

            # Formatting Date
            date_format = plt_date.DateFormatter('%d-%m-%Y')
            ax.xaxis.set_major_formatter(date_format)
            fig.autofmt_xdate()

            fig.tight_layout()

            ohlc['SMA5'] = ohlc['Close'].rolling(5).mean()
            ax.plot(ohlc['Date'], ohlc['SMA5'], color='green', label='SMA5')

            fig.suptitle('Daily Candlestick Chart of NIFTY50 with SMA5')

            plt.legend()
            plt.savefig("stock_crawler_graph_2.png")

            element.clear()
            element.setStyleSheet("border-image:url(stock_crawler_graph_2.png);")
        except TypeError :
            element.clear()
            element.setStyleSheet("border-image:url(stock_crawler_graph.png);")

    def plot_graph_function(self,element,data,name) :       # function สำหรับการ plot graph เเบบกราฟวงกลมของ rank graph
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


    def compare_thread_run(self,keyword ,api_sentiment ,web_sentiment) :  # เป็น function สำหรับ plot ข้อมูลต่างๆลงใน GUI หลังจากที่ทำ back end เสร็จเเละได้ข้อมูลครบเเล้ว

        result_func ,op_sentiment = api_sentiment ,web_sentiment

        #- - - - - - - - - - - - - - - - - - ส่วนของ api - - - - - - - - - - - - - - - - - -
        # ส่วนการ plot ข้อมูล word rank ของ api ลงใน GUI
        rank_file = pandas.read_csv(str(keyword) + '_NLP.csv')
        self.api_rank_show.clear()
        count = 1
        count_limit = 10
        for word,number in zip(rank_file['word'] ,rank_file['number']) :
            if count <= count_limit :
                number_use = str(number)
                self.api_rank_show.append(('{}.) ' + str(word) +"\n" + 'number : ' + number_use).format(count))
                count += 1
            else :
                break
        
        # ส่วนการ plot ข้อมูล word rank เเบบเป็น pie graph ของ api ลงใน GUI
        self.plot_graph_function(self.api_rank_graph ,rank_file ,'api_rank')

        # ส่วนของการ plot ข้อมูล sentiment ทั้งเเบบเป็นคำพูดเเละเเบบ pie graph ของ api ลงใน GUI
        self.api_sentiment_show.clear()
        self.sentiment_graph(self.api_sentiment_graph ,result_func ,"twitter_sentiment")
        temp_head = ["positive" ,"neutral" ,"negative"]
        for name ,number in zip(temp_head ,result_func) :
            number_use = str(number)
            self.api_sentiment_show.append(name + " : " + number_use + "\n")

        #- - - - - - - - - - - - - - - - - - ส่วนของ web - - - - - - - - - - - - - - - - - -

        # ส่วนการ plot ข้อมูล word rank ของ web ลงใน GUI
        rank_file_2 = pandas.read_csv('Web_crawler_NLP_4.csv')

        self.web_rank_show.clear()
        count = 1
        count_limit = 10
        for word,number in zip(rank_file_2['word'] ,rank_file_2['number']) :
            if count <= count_limit :
                number_use = str(number)
                self.web_rank_show.append(('{}.) ' + str(word) +"\n" + 'number : ' + number_use).format(count))
                count += 1
            else :
                break
        
        # ส่วนการ plot ข้อมูล word rank เเบบเป็น pie graph ของ web ลงใน GUI
        self.plot_graph_function(self.web_rank_graph,rank_file_2,'webside_rank')

        # ส่วนของการ plot ข้อมูล sentiment ทั้งเเบบเป็นคำพูดเเละเเบบ pie graph ของ web ลงใน GUI
        self.web_sentiment_show.clear()
        self.sentiment_graph(self.web_sentiment_graph ,op_sentiment ,"webside_sentiment")
        for name ,number in zip(temp_head ,op_sentiment) :
            number_use = str(number)
            self.web_sentiment_show.append(name + " : " + number_use + "\n")

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # อนุญาติให้กด compare ใหม่ได้เพราะ plot ข้อมูลเสร็จเเล้ว
        self.compare_button.setEnabled(True)


    def button_for_compare(self) :     # เป็น thread function สำหรับการทำ backend ในส่วนของ web เเละ api ในขณะที่ GUI ยังตอบสนองได้อยู่

        keyword = self.compare_input.text()  # keyword
        time_usable = self.format_time(self.time_label_all_1.date().toPyDate() ,self.time_label_all_2.date().toPyDate())  # ช่วงเวลา
        
        # เลือก function ที่จะทำ thread
        self.thread = QThread()
        self.compare_class = Compare_thread(keyword ,time_usable)
        self.compare_class.moveToThread(self.thread)

        # เงื่อนไขการเริ่มหรือจบ thread เเละเป็นตัวบอกว่าเมื่อจบ thread เเล้วทำอะไรต่อ
        self.thread.started.connect(self.compare_class.run)
        self.compare_class.finished.connect(self.thread.quit)
        self.compare_class.finished.connect(self.compare_class.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.compare_class.compare_plot_switch.connect(self.compare_thread_run)

        self.thread.start()
        self.compare_button.setEnabled(False)
        self.thread.finished.connect(lambda : self.compare_button.setEnabled(True))




#___________________________________________________________________________________________________________________________________________

def crawler_stock(key,start,end) :  # function สำหรับการดึงข้อมูล stock มาจาก yahoo โดยมีช่วงเวลาเเละ keyword เป็นตัวจำกัดเเละเก็บลงใน database

    try:      # ภาวะปกติ
        stock = pdr.get_data_yahoo(key, start = start, end = end)
        save = open("crawler_stock.csv","w",newline = "")
        save.write(stock.to_csv())
        save.close()
            
    except:   # ภาวะที่ดึงข้อมูลผิดพลาด
        save = open("crawler_stock.csv","w",newline = "")
        fieldnames = ["Date","High","Low","Open","Close","Volume","Adj Close"]
        writer_output = csv.DictWriter( save, fieldnames=fieldnames )
        writer_output.writeheader()
        save.close()
        print("Error:", sys.exc_info()[0])
        print("Description:", sys.exc_info()[1])

#___________________________________________________________________________________________________________________________________________

class Compare_thread(QObject) :        # class สำหรับทำในส่วนของ backend ทั้งหมดที่จำเป็นในการเเสดงข้อมูลของ GUI
    finished = pyqtSignal()
    compare_plot_switch = pyqtSignal(str ,list ,list)
    def __init__(self,keyword, time_usable) :   # ส่วนสำหรับ set ค่า input ที่ได้รับมา
        super().__init__()
        self.keyword = keyword
        self.time_usable = time_usable
    def run(self) :                # ส่วนสำหรับเริ่มทำงาน
        keyword = self.keyword
        time_usable = self.time_usable

        #- - - - - - - - - - - - - - - - - - -
        now = datetime.now()
        
        que1 = Queue.Queue()
        print("que1")
        que2 = Queue.Queue()
        print("que2")
        thread_1 = Thread(target = api_view , args = [keyword ,time_usable[0] ,time_usable[1]])    # ส่วนสำหรับตรวจสอบว่าข้อมูลของ api จาก database ที่ต้องการว่ามีข้อมูลครบทุกวันตามช่วงเวลาที่ต้องการหรือไม่ถ้าไม่ให้ update database
        thread_2 = Thread(target = lambda q ,arg1 ,arg2 ,arg3 : q.put(search_and_sentiment(arg1 ,arg2 ,arg3)), args = (que2 ,keyword ,time_usable[0] ,time_usable[1]))  # ส่วนสำหรับการดึงข้อมูลของ web จาก database ที่ต้องการเเละทำการตัดคำหา word rank เเละ sentiment ให้ด้วย
        thread_1.start()
        print("api : 1")
        thread_2.start()
        print("web : 1")
        #- - - - - - - - - - - - - - - - - - -
        thread_1.join()
        print("api : 2")

        # ส่วนสำหรับดึงข้อมูลของ api จาก database ที่ต้องการตามช่วงเวลาที่ต้องการหลังจาก update database เเล้ว
        key_file = pandas.read_csv(str(keyword) + '_api.csv')
        con_1 = key_file['time'] >= f'{time_usable[0]} 00:00:00'
        con_2 = key_file['time'] <= f'{time_usable[1]} 23:59:59'
        complete_file = key_file[con_1 & con_2]
        print("api : 3")

        #- - - - - - - - - - - - - - - - - - -
        # ส่วนสำหรับนำข้อมูลที่ได้มาตัดคำหา word rank ของ api
        thread_3 = Thread(target = NLP , args = [str(keyword) ,complete_file])
        # ส่วนสำหรับนำข้อมูลที่ได้มาหา sentiment ของ api
        func = sentiment()
        thread_4 = Thread(target = lambda q ,arg1 ,arg2 : q.put(func.sentiment_englist(arg1 ,arg2)), args = (que1 ,complete_file ,"tweet"))
        thread_3.start()
        print("api : 4")
        thread_4.start()
        print("api : 5")
        #- - - - - - - - - - - - - - - - - - -
        thread_3.join()
        print("api : 6")
        thread_4.join()
        print("api : 7")
        thread_2.join()
        print("web : 2")
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        result_func = que1.get()
        op_sentiment ,unusable = que2.get()
        
        finish = datetime.now()
        print("time use : ",finish - now)

        # เป็นส่วนบอกว่าได้ข้อมูลครบเเล้วให้จบ thread ได้เลยเเละนำข้อมูลไปให้ GUI
        self.compare_plot_switch.emit(keyword ,result_func , op_sentiment)
        self.finished.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    web = Compare()
    web.show()
    sys.exit(app.exec_())