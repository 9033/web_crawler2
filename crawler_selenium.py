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

        self.html_save(self.soup)


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

    def html_save(self, soup):

        save_path = os.path.join(BASE_DIR, 'html_save')
        try:
            os.mkdir(save_path)
        except:
            pass

        save_file_path = os.path.join(save_path, 'html_file.txt')

        with open(save_file_path, "w", encoding = "utf-8") as f:

            for line in soup:

                f.write(str(line) + '\n')


    def data_to_df(self, df):
 
        num = len(df)

        try:
            tbody = self.soup.findAll('tbody')
            #print(tbody)
        except AttributeError as error:
            logger.info(error)



        try:
            for i in range(len(tbody)):
                scope = ''
                rowspan_num = 0
                row_count = 0
                temp_list = []

                for trs in tbody[i].children:

                    if isinstance(trs, NavigableString):
                        continue

                    temp_column_name = ''
                    j = 0
                    for temp in trs.children:
                        if isinstance(temp, NavigableString):
                            continue

                        try:
                            rowspan_num = int(temp['rowspan'])
                            row_count = rowspan_num
                            temp_list = []
                        except:
                            pass

                        try: 
                            class_first = temp['class']
                            # print(class_first)
                            if class_first[0] == 'first':
                                scope = temp['scope']

                                if scope == 'col':
                                    temp_list = []
                            else:
                                pass


                        except:
                            pass
                        
                        # print("scope : ", scope)
                        # print("rowspan_num : ", rowspan_num)
                        # print("row_count : ", row_count)

                        if rowspan_num == 0:

                            if scope == 'row':

                                if j % 2 == 0:
                                    temp_column_name = temp.get_text().strip()
                                elif j % 2 == 1:
                                    if temp_column_name in df.columns:
                                        df.at[num, temp_column_name] = temp.get_text().strip()
                                    else:
                                        pass

                            else:
                                if j < 2:
                                    temp_list.append(temp.get_text().strip())    
                                elif j == 2:
                                    # print(temp_list)
                                    temp_join_list = [temp_list[0], temp_list[1]]
                                    temp_column_name = '-'.join(temp_join_list)
                                    if temp_column_name in df.columns:
                                        df.at[num, temp_column_name] = temp.get_text().strip()
                                    else:
                                        pass 
                                else:
                                    pass                                                                



                        elif rowspan_num == 2:
                            if row_count == rowspan_num:
                                # '발행주식수' 등 넣기 
                                temp_list.append(temp.get_text().strip())

                            else:
                                # print(temp_list)
                                temp_join_list = [temp_list[0], temp_list[j+1]]
                                temp_column_name = '-'.join(temp_join_list)
                                # print(temp_column_name)
                                if temp_column_name in df.columns:
                                    df.at[num, temp_column_name] = temp.get_text().strip()
                                else:
                                    pass

                        elif rowspan_num in [4,6]:
                            if row_count == rowspan_num:
                                if j in [0,2]:
                                    # "공모금액" 그리고 "주식수 (주)" 넣기 
                                    # "그룹별 배정" 그리고 "주식수 (주)" 넣기 
                                    temp_list.append(temp.get_text().strip())
                                else:
                                    pass

                            else:
                                if j == 0:

                                    temp_list.append(temp.get_text().strip())

                                elif j == 1:
                                    # print(temp_list)
                                    temp_join_list = [temp_list[0], temp_list[1], temp_list[(rowspan_num + 1)-row_count]]
                                    temp_column_name = '-'.join(temp_join_list)
                                    # print(temp_column_name)
                                    if temp_column_name in df.columns:
                                        df.at[num, temp_column_name] = temp.get_text().strip()
                                    else:
                                        pass
                                else:
                                    pass   

                        j += 1
                    # tr 달라질때 마다 
                    row_count -= 1 

            print(df) 
        
        except Exception as error:
            logger.info(error)
            return df 

        logger.info("row 추가 완료")
        return df          


class Crawler_Selenium(object):

    def __init__(self, url):

        self.url = url
        self.chromedriver_path = os.path.join(BASE_DIR, "chromedriver_win32", "chromedriver.exe")

    def run_chromedriver(self, chromedriver_path):

        try:
            driver = webdriver.Chrome(chromedriver_path)
            driver.get(self.url)
            logger.info("Selenium driver 생성")
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

            cbs4 = Crawler_BS4(driver)

            time.sleep(3)

            df = cbs4.data_to_df(df)

            time.sleep(3)

            # 사실상 신규상장기업현황 일때만 작동하게 됨 
            try:

                click_id = 'tabName'

                list_by_id = self.find_list_by_id(driver, click_id)

                for _id in list_by_id[1:]:
                    try:
                        _id.click()
                    except Exception as error:
                        logger.info(error)
                        continue

                    time.sleep(3)

                    cbs4 = Crawler_BS4(driver)

                    time.sleep(3)
            
                    df = cbs4.data_to_df(df)

                    time.sleep(3)
            except:
                pass

            driver.close()

            driver.switch_to.window(self.main_page)

            i += 1

            #이 부분은 작동 테스트 할 때만 
            # if i > 1:
            #     break

        return df


    def run(self, df, save_csv):
        logger.info("--------------------------------------------")  
        logger.info("process start")
        
        #driver 로딩
        driver = self.run_chromedriver(self.chromedriver_path)
        self.main_page = driver.current_window_handle
        time.sleep(3)

        #검색 시작 날짜 
        click_id = 'fromDate'
        day = '20201101'
        self.input_day(driver, click_id, day)

        time.sleep(2)

        #검색 종료 날짜
        click_id = 'toDate'
        day = '20210101'
        self.input_day(driver, click_id, day)

        time.sleep(2)

        #검색 누르기 
        class_name = 'btn-sprite.type-00.vmiddle.search-btn'
        search = self.find_by_class(driver, class_name)
        search.click()
        time.sleep(3)

        #전체 페이지 갯수 가져오기 
        #나중에 페이지를 넘기기 위해서 가져옴
        cbs4 = Crawler_BS4(driver)
        time.sleep(3)
        index_num, all_index_num = cbs4.find_index()
        logger.info("index_num : {} ".format(index_num))
        logger.info("all_index_num : {}".format(all_index_num))

        click_css = 'td.first'

        list_by_css = self.find_list_by_css(driver, click_css)
        time.sleep(3)



        df = self.click_popup_list(driver, list_by_css, df)
        time.sleep(3)



        next_page_xpath = '//*[@id="main-contents"]/section[2]/div[1]/a[{}]'.format(all_index_num + 3)

        while(index_num < all_index_num):
            
            index_num += 1
            next_page = driver.find_element_by_xpath(next_page_xpath)
            logger.info("index_num : {} ".format(index_num))
            
            next_page.click()
            time.sleep(3)

            self.main_page = driver.current_window_handle
            time.sleep(3)

            click_css = 'td.first'

            list_by_css = self.find_list_by_css(driver, click_css)
            time.sleep(3)

            df = self.click_popup_list(driver, list_by_css, df)
            time.sleep(3)

            
        print(df)

        df.to_csv(os.path.join(BASE_DIR, save_csv))

        self.down_chromedriver(driver)

        logger.info("process end")
        logger.info("--------------------------------------------")

if __name__ == "__main__":
    
    #예비심사기업
    url = "https://kind.krx.co.kr/listinvstg/listinvstgcom.do?method=searchListInvstgCorpMain"
    cs = Crawler_Selenium(url)
    df = DataFrame(columns = ['회사명', '심사청구일', '심사결과', '신규상장', '업종', '기업구분', '결산월', '상장(예정)주식수', '공모(예정)주식수', '상장주선인'])
    save_csv = 'test1.csv'
    cs.run(df, save_csv)
    #공모기업현황
    url = "https://kind.krx.co.kr/listinvstg/pubofrprogcom.do?method=searchPubofrProgComMain"
    cs = Crawler_Selenium(url)
    df = DataFrame(columns = ['회사명', '설립일', '업종', '결산월', '기업구분',\
        '수요예측일정', '공모청약일정', '상장(예정)일', '납입일', '희망공모가격',\
        '발행주식수-공모전 (주)', '발행주식수-공모후 (주)',\
        '공모금액-주식수 (주)-모집', '공모금액-주식수 (주)-매출', '공모금액-주식수 (주)-총액',\
        '그룹별배정-주식수 (주)-우리사주조합', '그룹별배정-주식수 (주)-기관투자자', '그룹별배정-주식수 (주)-일반투자자', '그룹별배정-주식수 (주)-기타', '그룹별배정-주식수 (주)-합계',\
        '사모(주관사인수)-주식수',\
        '상장주식수-보통주', '의무보유-보통주', '우리사주-보통주', '유통가능주식수-보통주'])
    save_csv = 'test2.csv'
    cs.run(df, save_csv)
    #신규상장기업현황 
    url = "https://kind.krx.co.kr/listinvstg/listingcompany.do?method=searchListingTypeMain"
    cs = Crawler_Selenium(url)
    df = DataFrame(columns= ['회사명', '청약경쟁률'])
    save_csv = 'test3.csv'
    cs.run(df, save_csv)