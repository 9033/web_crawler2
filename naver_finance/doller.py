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
        logger.info(url)
        try:
            html = urlopen(url)
        except Exception as error:
            logger.info(error)
            return None, None
         
        soup = BeautifulSoup(html.read(), 'html.parser')
        #print(soup)

        thead = soup.find('thead')
        tbody = soup.find('tbody')

        #print(tbody)

        return thead, tbody
    

    def data_to_df(self, data_list, df):

        #print(tbody)

        index = len(df)
        
        for i in range(len(data_list)):

            day = data_list[i][0]
            num = data_list[i][1]

            print(day)

            #print(day in df[self.df.columns[0]].values)
            if day in df[self.df.columns[0]].values:

                return df, False

            df.at[index, self.df.columns[0]] = day
            df.at[index, self.df.columns[1]] = num

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

    def read_csv(self, load_path):

        try:
            df = pd.read_csv(load_path, encoding = 'utf-8')
            logger.info("have file : {} ".format(load_path))
            # load 하면 column 이 하나 더 생겨서 삭제함 
            df = df.iloc[:,1:]
            return df
        except:
            logger.info("have not file : {} ".format(load_path))
            return self.df

    def run(self, save_csv):

        logger.info("run start")

        load_path = os.path.join('data', 'csv_file', save_csv)
        df = self.read_csv(load_path)

        print(df)
        print(df.columns)
        print(df.index)

        #425 가 마지막 
        # 기본값 1
        n = 10

        print(df[self.df.columns[0]])

        while(True):

            #print(n)

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

            # 만들때 테스트 할 때만, 그 외는 주석 처리
            if n > 20:
                break

        df = df.sort_values(by = self.df.columns[0], ascending = False)
        df = df.reindex(range(len(df)))
        print(df)
        print(df.columns)
        print(df.index)
        df.to_csv(os.path.join("data", "csv_file", save_csv))
        logger.info('save csv')

if __name__=="__main__":

    url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW"
    df = DataFrame(columns = ['day', '매매기준율'])

    naf = Naver_finance_crawler(url, df)

    save_csv = 'doller.csv'
    naf.run(save_csv)