import os
import time
import datetime 
import pandas as pd 
from pandas import DataFrame

from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

from libs.logging_process import Logging_process

logger = Logging_process('doller')

class Naver_finance_crawler(object):

    def __init__(self, url, df):

        self.url = url
        self.df = df

    def get_page_html(self, url, n):

        url = url + "&page={}".format(n)

        html = urlopen(url)
        soup = BeautifulSoup(html.read(), 'html.parser')

        thead = soup.find('thead')
        tbody = soup.find('tbody')

        #print(thead)

        return thead, tbody
    

    def data_to_df(self, data_list, df):

        #print(tbody)

        index = len(df)
        
        for i in range(len(data_list)):

            date = data_list[i][0]
            num = data_list[i][1]

            print(date)

            if date in df.index:

                return df, False

            #df.at[date, self.df.columns[0]] = date
            df.at[date, self.df.columns[0]] = num

            index += 1

        return df, True

    def tbody_data(self, tbody):

        out_list = []

        for tr in tbody.children:

            if isinstance(tr, NavigableString):
                continue

            date = tr.find('td' , {'class' : 'date'})
            num = tr.find('td', {'class' : 'num'})

            date = date.get_text().strip()
            date = date.replace('.', '-')
            #date = datetime.datetime.strptime(date, "%Y-%m-%d")

            num = num.get_text().strip()
            num = num.replace(',', '') 
            num = float(num)
            

            out_list.append((date, num))  

        return out_list

    def read_csv(self, save_csv):

        try:
            df = pd.read_csv("data\\csv_file\\"+save_csv, encoding = 'utf-8')
            logger.info("have file : {} ".format(save_csv))
            return df
        except:
            logger.info("have not file : {} ".format(save_csv))
            return self.df

    def run(self, save_csv):

        logger.info("run")

        df = self.read_csv(save_csv)

        df.index = df.iloc[:, 0]
        df = df.iloc[:,1:]
        # new_df = DataFrame(index = df.iloc[:, 0].values, columns=self.df.columns)
        # print(new_df)
        # new_df[self.df.columns[0]] = df[self.df.columns[0]]
        # print(new_df)
        # df = new_df
        print(df)
        print(df.columns)
        print(df.index)

        #425 가 마지막 

        n = 7

        print(df[self.df.columns[0]])

        while(False):

            print(n)

            try:
                _, tbody = self.get_page_html(self.url, n)
            except Exception as error:
                logger.info(error)
                break
            
            #print(tbody)

            out_list = self.tbody_data(tbody)

            # 더 이상 데이터가 없으면 중지함 
            if len(out_list) < 1:
                break

            df, conti = self.data_to_df(out_list, df)

            if not conti:
                break

            time.sleep(0.5)

            n += 1

            if n > 15:
                break

        #df = df[self.df.columns[0]].sort_values(ascending = False)
        # print(df)
        # print(df.columns)
        # print(df.index)
        #df.to_csv(os.path.join("data", "csv_file", save_csv))
        #df.to_csv(save_csv)
        logger.info('save csv')

if __name__=="__main__":

    url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW"
    df = DataFrame(columns = ['매매기준율'])

    naf = Naver_finance_crawler(url, df)

    save_csv = 'doller.csv'
    naf.run(save_csv)