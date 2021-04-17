# -*- coding: utf-8 -*-
import os 
import csv
import time 
import logging
import pandas as pd 
from pandas import DataFrame
from bs4 import BeautifulSoup, NavigableString
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

#log console 출력 
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

#log file 저장 
file_handler = logging.FileHandler("test.log", encoding = 'utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class Crawler_BS4(object):

    def __init__(self, driver):

        self.html = driver.page_source
        self.soup = BeautifulSoup(self.html, "html.parser")


    def find_index(self):
        
        all_index = self.soup.find('div', {'class' : 'info'})
        #print(all_index)
        index_num = all_index.get_text().strip()
        index_num, all_index_num = index_num.split('\n')[0].split()[-1].split('/')
        index_num = int(index_num)
        all_index_num = int(all_index_num)
        #print(index_num)
        #print(all_index_num)

        return index_num, all_index_num

    def run(self):

        try:
            co_name = self.soup.findAll('tr', {'class' : 'first'})
        #print(co_name)
        except Exception as error:
            logger.info(error)

        for temp in co_name:
            try:
                temp = temp.find('td')
                temp_text = temp.get_text().strip()
                logger.info(temp_text)
            except AttributeError as error:
                logger.info(error)

    def InvstgCorp(self, df):
        """예비심사기업"""

        num = len(df)

        try:
            tbody = self.soup.findAll('tbody')
            #print(tbody)
        except AttributeError as error:
            logger.info(error)

        try:
            for i in range(len(tbody)):

                for trs in tbody[i].children:

                    if isinstance(trs, NavigableString):
                        continue

                    temp_column_name = ''
                    j = 0
                    for temp in trs.children:
                        if isinstance(temp, NavigableString):
                            continue
                        #print(temp)

                        if j % 2 == 0:
                            temp_column_name = temp.get_text().strip()
                        elif j % 2 == 1:
                            if temp_column_name in df.columns:
                                df.at[num, temp_column_name] = temp.get_text().strip()
                            else:
                                pass

                        j += 1

            print(df) 
        
        except AttributeError as error:
            logger.info(error)

      

        return df


    def PubofrProgCom(self, df):
        """공모기업현황"""

        num = len(df)

        try:
            tbody = self.soup.findAll('tbody')
            #print(tbody)
        except AttributeError as error:
            logger.info(error)

        try:
            for i in range(len(tbody)):

                rowspan_num = 0
                remain_num = 0
                temp_list = []

                for trs in tbody[i].children:

                    if isinstance(trs, NavigableString):
                        continue

                    temp_column_name = ''
                    j = 0
                    for temp in trs.children:
                        if isinstance(temp, NavigableString):
                            continue
                        #print(temp)

                        # if temp['rowspan'] is not None:
                        #     rowspan_num = int(temp['rowspan'])
                        #     remain_num = rowspan_num
                        # else:
                        #     pass
                        try:
                            rowspan_num = int(temp['rowspan'])
                            logger.info("rowspan_num : {} ".format(rowspan_num))
                            remain_num = rowspan_num
                            logger.info("remain_num : {} ".format(remain_num))
                        except Exception as error:
                            logger.info(error)
                            pass

                        if rowspan_num == 0:

                            if j % 2 == 0:
                                temp_column_name = temp.get_text().strip()
                            elif j % 2 == 1:
                                if temp_column_name in df.columns:
                                    df.at[num, temp_column_name] = temp.get_text().strip()
                                else:
                                    pass

                        elif remain_num == rowspan_num:
                            temp_list.append(temp.get_text().strip())

                        elif remain_num < rowspan_num:
                            temp_join_list = [temp_list[0], temp_list[j+1]]
                            temp_column_name = '-'.join(temp_join_list)
                            if temp_column_name in df.columns:
                                df.at[num, temp_column_name] = temp.get_text().strip()
                            else:
                                pass                           




                        j += 1
                        #print(df)
                    logger.info("temp_list length : %d ", len(temp_list))

                    remain_num -= 1

                    if remain_num == 0:
                        rowspan_num = 0
                        temp_list = []

            print(df) 
        
        except AttributeError as error:
            logger.info(error)
        

        return df 



 
            


class Crawler_Selenium(object):

    def __init__(self, url):

        self.url = url
        self.chromedriver_path = os.path.join(BASE_DIR, "chromedriver_win32", "chromedriver.exe")

    def run_chromedriver(self, chromedriver_path):

        try:
            driver = webdriver.Chrome(chromedriver_path)
            driver.get(self.url)
            logger.info("driver 생성")
        except Exception as error:
            logging.info(error)

        return driver

    def down_chromedriver(self, driver):

        driver.quit()

    def find_by_id(self, driver, click_id):

        find_id = driver.find_element_by_id(click_id)

        return find_id

    def find_list_by_id(self, driver, click_id):

        list_by_id = driver.find_elements_by_id(click_id)

        return list_by_id

    def find_list_by_css(self, driver, click_css):

        list_by_css = driver.find_elements_by_css_selector(click_css)

        return list_by_css

    def find_by_class(self, driver, class_name):

        find_class = driver.find_element_by_class_name(class_name)

        return find_class

    def find_list_by_class(self, driver, class_name):

        list_by_class = driver.find_elements_by_class_name(class_name)

        return list_by_class

    def input_day(self, driver, click_id, day):
        logger.info("click_id : {} ".format(click_id))
        logger.info("day {} ".format(day))

        try:
            find_id = self.find_by_id(driver, click_id)
            find_id.clear()
            find_id.send_keys(day)
            time.sleep(2)
            find_id.send_keys(Keys.ENTER)
        except Exception as error:
            logger.info(error)
            self.down_chromedriver(driver)


    def click_popup_list(self, driver, _list, df):

        i = 0

        for i in range(len(_list)):

            try:
                _list[i].click()
            except Exception as error:
                logger.info(error)
                continue

            for handle in driver.window_handles:
                if handle != self.main_page:
                    new_page = handle

            driver.switch_to.window(new_page)

            time.sleep(3)

            click_id = 'tabName'

            list_by_id = self.find_list_by_id(driver, click_id)

            cbs4 = Crawler_BS4(driver)

            time.sleep(3)

            #df = cbs4.InvstgCorp(df)
            df = cbs4.PubofrProgCom(df)

            time.sleep(3)

            # for _id in list_by_id[1:]:
            #     try:
            #         _id.click()
            #     except Exception as error:
            #         logger.info(error)
            #         continue

            #     time.sleep(3)

            #     cbs4 = Crawler_BS4(driver)

            #     time.sleep(3)

            #     cbs4.run()

            #     time.sleep(3)





            driver.close()

            driver.switch_to.window(self.main_page)

            i += 1


            if i > 1:
                break

        return df


    def run(self):
        logger.info("--------------------------------------------")  
        logger.info("process start")
        
        #driver 로딩
        driver = self.run_chromedriver(self.chromedriver_path)
        self.main_page = driver.current_window_handle
        time.sleep(3)

        # #검색 시작 날짜 
        # click_id = 'fromDate'
        # day = '20201101'
        # self.input_day(driver, click_id, day)

        # time.sleep(2)

        # #검색 종료 날짜
        # click_id = 'toDate'
        # day = '20210101'
        # self.input_day(driver, click_id, day)

        # time.sleep(2)

        # #검색 누르기 
        # class_name = 'btn-sprite.type-00.vmiddle.search-btn'
        # search = self.find_by_class(driver, class_name)
        # search.click()
        # time.sleep(3)

        #전체 페이지 갯수 가져오기 
        #나중에 페이지를 넘기기 위해서 가져옴
        cbs4 = Crawler_BS4(driver)
        time.sleep(3)
        index_num, all_index_num = cbs4.find_index()
        logger.info("index_num : {} ".format(index_num))
        logger.info("all_index_num : {}".format(all_index_num))


        #click_css = 'img.vmiddle.legend'
        click_css = 'td.first'

        list_by_css = self.find_list_by_css(driver, click_css)
        time.sleep(3)

        # df = DataFrame(columns = ['회사명', '심사청구일', '심사결과', '신규상장', '업종', '기업구분', '결산월', '상장(예정)주식수', '공모(예정)주식수', '상장주선인'])
        df = DataFrame(columns = ['회사명', '설립일', '업종', '결산월', '기업구분',\
             '수요예측일정', '공모청약일정', '상장(예정)일', '납입일', '희망공모가격',\
             '발행주식수-공모전 (주)', '발행주식수-공모후 (주)',\
             '공모금액-모집', '공모금액-매출', '공모금액-총액',\
             '그룹별배정-우리사주조합', '그룹별배정-기관투자자', '그룹별배정-일반투자자', '그룹별배정-기타', '그룹별배정-합계'\
             '사모 (주관사인수)'])

        df = self.click_popup_list(driver, list_by_css, df)
        time.sleep(3)



        next_page_xpath = '//*[@id="main-contents"]/section[2]/div[1]/a[{}]'.format(all_index_num + 3)

        while(index_num < all_index_num):
            
            index_num += 1
            next_page = driver.find_element_by_xpath(next_page_xpath)
            logger.info("index_num : {} ".format(index_num))
            
            # if next_page.find_element_by_class_name()
            next_page.click()
            time.sleep(3)

            self.main_page = driver.current_window_handle
            time.sleep(3)

            #click_css = 'img.vmiddle.legend'
            click_css = 'td.first'

            list_by_css = self.find_list_by_css(driver, click_css)
            time.sleep(3)

            df = self.click_popup_list(driver, list_by_css, df)
            time.sleep(3)

            
        print(df)

        df.to_csv(os.path.join(BASE_DIR, "test.csv"))

        self.down_chromedriver(driver)

        logger.info("process end")
        logger.info("--------------------------------------------")

if __name__ == "__main__":
    
    #예비심사기업
    # url = "https://kind.krx.co.kr/listinvstg/listinvstgcom.do?method=searchListInvstgCorpMain"
    # cs = Crawler_Selenium(url)
    # cs.run()
    #공모기업현황
    url = "https://kind.krx.co.kr/listinvstg/pubofrprogcom.do?method=searchPubofrProgComMain"
    cs = Crawler_Selenium(url)
    cs.run()
    #신규상장기업현황 
    # url = "https://kind.krx.co.kr/listinvstg/listingcompany.do?method=searchListingTypeMain"
    # cs = Crawler_Selenium(url)
    # cs.run()