import unittest
import itertools
import pandas
from twiter_api import *
from crawler import *
from crawler_update import*


class MyTest_api(unittest.TestCase) :      # test twiter_api class
    def test_api_view(self) :            # normal test
        myCal = api_view("covid" ,"2021-04-24" ,"2021-04-26")
        self.assertNotEqual(myCal, 0)

    def test_api_view_2(self) :              # error test
        myCal_1 = api_view("covid" ,"2021-04-26" ,"2021-04-24")
        self.assertNotEqual(myCal_1, 0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_data_tweet(self) :         # normal test
        myCal_2 = Data_twitter("covid")
        self.assertNotEqual(len(myCal_2.old_data), 0)

    def test_data_tweet_2(self) :       # normal test
        myCal_2 = Data_twitter("covid")
        test1 = myCal_2.get_data()
        self.assertIsNotNone(myCal_2.test)

    def test_data_tweet_3(self) :     # normal test
        myCal_2 = Data_twitter("covid")
        test2 = myCal_2.get_data_by_time("2021-04-26")
        self.assertIsNotNone(myCal_2.test)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_top_trends_tweet(self) :      # normal test
        myCal_3 = top_trends_tweet()
        self.assertNotEqual(myCal_3, 0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_nlp(self) :        # normal test
        data_test = pandas.read_csv('covid_api.csv')
        con_test1 = data_test['time'] >= '2021-04-25 00:00:00'
        con_test2 = data_test['time'] <= '2021-04-26 23:59:59'
        compare_test = data_test[con_test1 & con_test2]
        myCal_4 = NLP("covid" ,compare_test)
        result = myCal_4.detection_lang('House Republicans Propose New State Budget Structure')
        self.assertEqual(type(result), str)

    def test_nlp_2(self) :          # error test
        data_test = pandas.read_csv('covid_api.csv')
        con_test1 = data_test['time'] >= '2021-04-25 00:00:00'
        con_test2 = data_test['time'] <= '2021-04-26 23:59:59'
        compare_test = data_test[con_test1 & con_test2]
        myCal_4 = NLP("covid" ,compare_test)
        result = myCal_4.detection_lang(20)
        self.assertEqual(type(result), str)

    def test_nlp_3(self) :      # normal test
        data_test = pandas.read_csv('covid_api.csv')
        con_test1 = data_test['time'] >= '2021-04-25 00:00:00'
        con_test2 = data_test['time'] <= '2021-04-26 23:59:59'
        compare_test = data_test[con_test1 & con_test2]
        myCal_4 = NLP("covid" ,compare_test)
        result = myCal_4.word_rank({'word' : 4, 'number': 9, 'covid' : 14, 'hat' : 3})
        ans = {'covid' : 14, 'number': 9, 'word' : 4, 'hat' : 3}
        self.assertEqual(result, ans)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_time_check(self) :       # normal test
        test_dic = {'time': ["2021-04-20", "2021-04-22", "2021-04-25", "2021-04-26"]}
        myCal_5 = time_check("2021-04-19" ,"2021-04-26", test_dic)
        self.assertEqual(myCal_5, ["2021-04-19", "2021-04-21", "2021-04-23", "2021-04-24"])

    def test_time_check_2(self) :           # error test
        test_dic = {'time': ["2021-04-20", "2021-04-22", "2021-04-25", "2021-04-26"]}
        myCal_5 = time_check("2021-04-26" ,"2021-04-19", test_dic)
        self.assertEqual(myCal_5, ["2021-04-19", "2021-04-21", "2021-04-23", "2021-04-24"])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_geopy(self) :        # normal test
        test_dic = {'places': ["1 Apple Park Way, Cupertino, CA"]}
        df = pandas.DataFrame(data = test_dic)
        myCal_6 = geopy2(df)
        self.assertEqual(myCal_6, [("1 Apple Park Way, Cupertino, CA", 37.3348469, -122.01139215737962)])

#_________________________________________________________________________________________________________________________________________________________

class MyTest_web(unittest.TestCase) :               # test twiter_api class
    def test_sentiment(self) :             # normal test
        test_dic = {'content': ["A league of their own (or a section, anyway) for baseball fans who are fully vaccinated.",
                    "No evidence that Pfizer or Moderna vaccines are unsafe during pregnancy, a preliminary study says.",
                    "Biden asks U.S. employers to give workers paid time off to get vaccinated.",
                    "New coronavirus cases around the world reached a new weekly record, according to the W.H.O.",
                    "The Los Angeles schools chief will leave in June, after leading through the pandemic.",
                    "An unvaccinated worker set off an outbreak at a U.S. nursing home where most residents were immunized.",
                    "Silence is golden, this year, at least, as British town criers compete for glory."]}
        myCal_7 = sentiment()
        sen = myCal_7.sentiment_englist(test_dic, "content")
        self.assertEqual(sen, [3, 4, 0])

    def test_sentiment_2(self) :          # normal test
        test = "A league of their own (or a section, anyway) for baseball fans who are fully vaccinated."
        myCal_8 = sentiment()
        out = myCal_8.nlp_function(test)
        self.assertEqual(out, ['league', 'section', 'baseball', 'fans', 'fully', 'vaccinated'])

    def test_sentiment_3(self) :           # normal test
        test = "A league of their own (or a section, anyway) for baseball fans who are fully vaccinated."
        myCal_9 = sentiment()
        out = myCal_9.detection_lang(test)
        self.assertEqual(out, "en")

    def test_sentiment_3(self) :         # normal test
        test = "เธอได้เผยต่ออีกว่าเจ้าหญิงชาร์ลอตต์วัย 5 ขวบ และพี่ชายอย่างเจ้าชายจอร์จวัย 7 ขวบนั้น ไม่ได้รับอนุญาตให้ใช้เงินอย่างสุรุ่ยสุร่าย แต่ทั้งสองมีงบจำกัดในการซื้อของและยังต้องจ่ายด้วยเงินส่วนตัวของตัวเอง"
        myCal_10 = sentiment()
        out1 = myCal_10.nlp_function(test)
        out2 = myCal_10.sentiment_thai(out1)
        self.assertEqual(out2, [0, 0, 1])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_search_and_sentiment(self) :         # normal test
        myCal_11, myCal_12 = search_and_sentiment("covid" ,"2021-04-20" ,"2021-04-21")
        self.assertEqual((myCal_11 , len(myCal_12)), ([4, 0, 0] , 5))

    def test_Crawler_NLP(self) :                # normal test
        sen , test_dic = search_and_sentiment("covid" ,"2021-04-20" ,"2021-04-21")
        myCal_14 = Crawler_NLP(test_dic ,"content")
        rank = myCal_14.all_word
        top_rank = dict(itertools.islice(rank.items(), 10))
        self.assertEqual(top_rank, {'said': 105, 'Covid': 54, 'patients': 46, 'people': 43, 'state': 43, 'vaccine': 40, 'Indian': 40, 'government': 39, 'oxygen': 38, 'News': 37})


if __name__ == '__main__' :
    unittest.main()