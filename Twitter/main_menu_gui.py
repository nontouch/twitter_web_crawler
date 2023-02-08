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

from compare_gui import *
from twiter_api import *
from crawler import *
from twiter_crawler_gui import*


class Main_menu_GUI(QWidget) :          # class GUI สำหรับ menu ว่าจะทำโหมดอะไรเชื่อมระหว่าง twit and crawler GUI กับ compare GUI  
    switch_window = QtCore.pyqtSignal()
    switch_window_2 = QtCore.pyqtSignal()
    def __init__(self) :              # ส่วนสำหรับการตั้งค่าหน้าต่าง GUI
        super().__init__()
        self.title = ' Twitter and web crawler menu '
        self.image = 'menu_background.png'
        self.icon = "Shrimp-front.png"
        self.left = 300 
        self.top = 100
        self.width = 1000
        self.height = 600

        self.palette = QPalette()
        self.vbox = QVBoxLayout()

        self.initUI()

    def initUI(self) :          # ส่วนสำหรับการวาง element ต่างๆในหน้าต่าง GUI
        # ส่วนสำหรับตั้งชื่อ title เเละ set ขนาดของ GUI
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # ส่วนสำหรับวาง background ของ GUI
        background = QImage(self.image)
        background_side = background.scaled(QSize(self.width,self.height))  
        self.palette.setBrush(QPalette.Window, QBrush(background_side))
        self.setPalette(self.palette)

        # ส่วนหัวข้อของ GUI
        self.label_head = QLabel('Twitter and web crawler menu', self)
        self.label_head.move(200, 10)
        self.label_head.setFont(QFont('Arial', 30))

        # ปุ่มสำหรับกดไป twit and crawler GUI
        self.button_tw_web = QPushButton('twit and' + '\n' + 'web mode', self)
        self.button_tw_web.resize(200,80)
        self.button_tw_web.move(50,150)
        self.button_tw_web.setFont(QFont('Times', 20)) 
        self.button_tw_web.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_tw_web.setIcon(QIcon(self.icon))

        # ปุ่มสำหรับกดไป compare GUI
        self.button_compare = QPushButton('compare' + '\n' + 'mode', self)
        self.button_compare.resize(200,80)
        self.button_compare.move(50,300)
        self.button_compare.setFont(QFont('Times', 20)) 
        self.button_compare.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_compare.setIcon(QIcon(self.icon))

        # ส่วนสำหรับปุ่มกดปิด GUI
        self.button_exit = QPushButton('Exit', self)
        self.button_exit.resize(200,80)
        self.button_exit.move(50,450)
        self.button_exit.setFont(QFont('Times', 20)) 
        self.button_exit.setStyleSheet("QPushButton" "{" "background-color : lightyellow;" "}" "QPushButton::hover" "{" "background-color : yellow;" "}" "QPushButton::pressed" "{" "background-color : red;" "}")
        self.button_exit.setIcon(QIcon(self.icon))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.button_tw_web.clicked.connect(self.twiter_crawler_page)
        self.button_compare.clicked.connect(self.compage_page)
        self.button_exit.clicked.connect(QApplication.instance().quit)

    def twiter_crawler_page(self) :       # เป็น function ที่เชื่อมต่อ GUI นี้กับ twit and crawler GUI
        self.switch_window.emit()

    def compage_page(self) :               # เป็น function ที่เชื่อมต่อ GUI นี้กับ compare GUI
        self.switch_window_2.emit()

#_________________________________________________________________________________________________________________________________________________________


class Gui_controller() :     # class สำหรับ ควบคุมว่าตอนนี้จะให้ run GUI อันไหน
    def __init__(self) :
        pass
    def main_menu(self) :       # เป็น function สำหรับ run menu GUI
        self.menu = Main_menu_GUI()
        self.menu.switch_window.connect(self.twitter_web_mode)
        self.menu.switch_window_2.connect(self.compare_mode)
        self.menu.show()
    def twitter_web_mode(self) :        # เป็น function สำหรับ run twit and crawler GUI
        top_trends_tweet()
        self.tw_web = Api_and_crawler_GUI()
        self.tw_web.switch_window.connect(self.back_mode_1)
        self.menu.close()
        self.tw_web.show()
    def compare_mode(self) :          # เป็น function สำหรับ run compare GUI
        self.comp = Compare()
        self.comp.switch_window.connect(self.back_mode_2)
        self.menu.close()
        self.comp.show()
    def back_mode_1(self) :      # เป็น function ย้อนกลับไปหน้า menu GUI สำหรับ twit and crawler GUI
        self.tw_web.close()
        self.main_menu()

    def back_mode_2(self) :      # เป็น function ย้อนกลับไปหน้า menu GUI สำหรับ compare GUI
        self.comp.close()
        self.main_menu()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    menu = Gui_controller()
    menu.main_menu()
    sys.exit(app.exec_())