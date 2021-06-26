import os 
import time
import pandas as pd
from pandas import DataFrame

from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

from libs.logging_process import Logging_process
from libs.selenium_process import Selenium_process

logger = Logging_process('scrap_macro_economics_test')

class Naver_finance_crawler(object):
    """naver finance 에 있는 항목들을 크롤링하는데 사용함,
    Selenium 사용하지 않고 크롤링 함 """

    def __init__(self, df, url):

        self.df = df
        self.url = url

    def get_page_html(self, page_num):

        url = self.url + "&page={}".format(page_num)
        logger.info(url)

        try:
            html = urlopen(url)

        except Exception as error:
            logger.info(error)
            return None, None 

        soup = BeautifulSoup(html.read(), 'html.parser')

        thead = soup.find('thead')
        tbody = soup.find('tbody')

        return thead, tbody

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

    def data_to_df(self, df, data_list):

        #print(tbody)

        index = len(df)
        
        for i in range(len(data_list)):

            day = data_list[i][0]
            num = data_list[i][1]

            print(day)

            #print(day in df[self.df.columns[0]].values)
            if day in df[self.df.columns[0]].values:

                return df

            df.at[index, self.df.columns[0]] = day
            df.at[index, self.df.columns[1]] = num

            index += 1

        return df

    def run(self, page):
        """page 수 만큼 반복하여 크롤링하기"""

        df = self.df 


        for page_num in range(1, page + 1):
            # page 는 1부터 시작함 

            try:
                _, tbody = self.get_page_html(page_num)
            except Exception as error:
                logger.info(error)
                return None 

            out_list = self.tbody_data(tbody)

            df = self.data_to_df(df ,out_list)

            # 혹시 모를 ip 차단을 피하기 위해서 쉬어가는 타임
            time.sleep(1)
        
        df = df.sort_values(by = self.df.columns[0], ascending = False)

        return df

class Crawler_BS4(object):
    """Selenium driver를 이용한 stock index crawler 부분"""

    def __init__(self, driver):
        """driver를 받아 BeautifulSoup 객체를 생성한다."""

        self.html = driver.page_source
        self.soup = BeautifulSoup(self.html, "html.parser")
        logger.info("soup 생성")

    def get_page_html(self):

        try:
            soup = self.soup

            thead = soup.find('thead')
            tbody = soup.findAll('tbody')[1]
        except Exception as error:
            logger.info(error)
            return None, None

        return thead, tbody

    def get_data(self, tbody):
        
        out_list = []

        for tr in tbody.children:
        
            if isinstance(tr, NavigableString):
                continue

            day = tr.find('td', {'class' : 'tb_td'})            
            day = day.get_text().strip()
            day = day.replace('.', '-')

            close_point = tr.find('td', {'class' : 'tb_td2'})
            close_point = close_point.get_text().strip()
            close_point = close_point.replace(',', '')
            close_point = float(close_point)

            open_point = tr.find('td', {'class' : 'tb_td4'})
            open_point = open_point.get_text().strip()
            open_point = open_point.replace(',', '')
            open_point = float(open_point)

            high_point = tr.find('td', {'class' : 'tb_td5'})
            high_point = high_point.get_text().strip()
            high_point = high_point.replace(',', '')
            high_point = float(high_point)

            low_point = tr.find('td', {'class' : 'tb_td6'})
            low_point = low_point.get_text().strip()
            low_point = low_point.replace(',', '')
            low_point = float(low_point)

            out_list.append((day, close_point, open_point, high_point, low_point))

        return out_list
                


    def data_to_df(self, df, data_list):

        index = len(df)
                
        for i in range(len(data_list)):

            day = data_list[i][0]
            close_point = data_list[i][1]
            open_point = data_list[i][2]
            high_point = data_list[i][3]
            low_point = data_list[i][4]

            if day in df[df.columns[0]].values:

                return df, False

            df.at[index, df.columns[0]] = day
            df.at[index, df.columns[1]] = close_point
            df.at[index, df.columns[2]] = open_point
            df.at[index, df.columns[3]] = high_point
            df.at[index, df.columns[4]] = low_point

            index += 1

        return df, True

    def process(self, df):

        _, tbody = self.get_page_html()
        #print(tbody)

        out_list = self.get_data(tbody)
        #print(out_list)

        df = self.data_to_df(df, out_list)

        return df 

class World_Stock_Market(object):
    """naver finance 에서 주가지수 항목들은 크롤링할때
    Selenium 을 사용함"""

    def __init__(self, df, url):
        logger.info("Creating Selenium Object")

        self.sp = Selenium_process(url)

        logger.info("Selenium driver loading")
        self.driver = self.sp.run_chromedriver()

        self.driver.implicitly_wait(5)
        self.main_page = self.driver.current_window_handle

        self.df = df

    def run(self, page):

        # scrap 할 page 갯수
        max_count_page = page
        # scrap 한 page 갯수
        count_page = 0

        stop = False 
                    
        #stock page 보면 10 page 씩 묶여있다. 
        #처음에는 1 ~ 10 page 있고, 다음 눌러야 11 ~ 20 page 가 나온다.
        # page xpath 구하는 숫자
        view_page = 0

        while(stop == False):

            for num in range(1,11):

                page_num = view_page * 10 + num

                page_xpath = '//*[@id="dayLink{}"]'.format(page_num)
                page = self.driver.find_element_by_xpath(page_xpath)         

                try:
                    page.click()
                except Exception as error:
                    logger.info(error)
                    stop = True
                    break                
            
                self.main_page = self.driver.current_window_handle

                try:
                    cbs4 = Crawler_BS4(self.driver)

                    #time.sleep(3)
                except Exception as error:
                    logger.info(error)
                    stop = True
                    break

                try:
                    self.df, conti = cbs4.process(self.df)
                    logger.info('id="dayLink{}" 의 데이터를 DataFrame 으로 저장함'.format(page_num))
                except Exception as error:
                    logger.info(error)
                    stop = True
                    break

                logger.info('id="dayLink{}" 처리 완료'.format(page_num))

                # scrap 끝났으니까 
                count_page += 1

                # 혹시 모를 ip 차단을 피하기 위해서 쉬어가는 타임 
                time.sleep(1)

                # scrap page 갯수가 만족 되었으면 중지함 
                if count_page > max_count_page:
                    stop = True
                    break

            #for 문 완료됨, 그럼 이제 다음 view_page로 넘어감
            
            class_name = 'next'
            next_page = self.driver.find_element_by_class_name(class_name)

            try:
                next_page.click()
            except Exception as error:
                logger.info(error)
                break  

            self.main_page = self.driver.current_window_handle

            view_page += 1 

        self.df = self.df.sort_values(by = self.df.columns[0], ascending = False)

        self.sp.down_chromedriver(self.driver)

        return self.df


class scrap_macro_economics(object):
    """항목마다 DB table 생성 & 크롤링 함수들이 있음"""

    def __init__(self):
        pass

    def scrap_exchange_rate(self, name, url, page):
        "환율 크롤링 함수"
        df = DataFrame(columns = ['날짜', '매매기준율'])

        # create table (name) 

        # select max_date from table (name)

        self.nfc = Naver_finance_crawler(df, url)

        df = self.nfc.run(page) 

        print(df)

        save_file_path = os.path.join("data", "csv_file", "exchange_rate")
        os.makedirs(save_file_path, exist_ok = True)

        df.to_csv(os.path.join(save_file_path, name + ".csv"))

        # update table (name)

    def scrap_interest_rate(self, name, url, page):
        "금리 크롤링 함수"
        df = DataFrame(columns = ['날짜', '종가'])

        # create table (name) 

        # select max_date from table (name)

        self.nfc = Naver_finance_crawler(df, url)

        df = self.nfc.run(page) 

        print(df)

        save_file_path = os.path.join("data", "csv_file", "interest_rate")
        os.makedirs(save_file_path, exist_ok = True)

        df.to_csv(os.path.join(save_file_path, name + ".csv"))

        # update table (name)

    def scrap_gold_oil(self, name, url, page):
        "금&석유 크롤링 함수"
        df = DataFrame(columns = ['날짜', '종가'])

        # create table (name) 

        # select max_date from table (name)

        self.nfc = Naver_finance_crawler(df, url)

        df = self.nfc.run(page) 

        print(df)

        save_file_path = os.path.join("data", "csv_file", "gold_oil")
        os.makedirs(save_file_path, exist_ok = True)

        df.to_csv(os.path.join(save_file_path, name + ".csv"))

        # update table (name)

    def scrap_non_ferrous_metal(self, name, url, page):
        "비철금속 크롤링 함수"
        df = DataFrame(columns = ['날짜', '종가'])

        # create table (name) 

        # select max_date from table (name)

        self.nfc = Naver_finance_crawler(df, url)

        df = self.nfc.run(page) 

        print(df)

        save_file_path = os.path.join("data", "csv_file", "non_ferrous_metal")
        os.makedirs(save_file_path, exist_ok = True)

        df.to_csv(os.path.join(save_file_path, name + ".csv"))

        # update table (name) 

    def scrap_agricultural_product(self, name, url, page):
        "농산물 크롤링 함수"
        df = DataFrame(columns = ['날짜', '종가'])

        # create table (name) 

        # select max_date from table (name)

        self.nfc = Naver_finance_crawler(df, url)

        df = self.nfc.run(page) 

        print(df)

        save_file_path = os.path.join("data", "csv_file", "agricultural_product")
        os.makedirs(save_file_path, exist_ok = True)

        df.to_csv(os.path.join(save_file_path, name + ".csv"))

        # update table (name)
           

    def scrap_global_stock(self, name, url, page):
        '''외국 주요 주가지수 크롤링 함수'''

        df = DataFrame(columns = ['일자', '종가', '시가', '고가', '저가'])

        self.wsm = World_Stock_Market(df, url)

        # create table (name) 

        # select max_date from table (name)

        df = self.wsm.run(page)

        print(df)

        save_file_path = os.path.join("data", "csv_file", "global_stock")
        os.makedirs(save_file_path, exist_ok = True)

        df.to_csv(os.path.join(save_file_path, name + ".csv"))

        # update table (name)    




if __name__=="__main__":

    pass 