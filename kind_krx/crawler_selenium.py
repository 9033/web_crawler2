# -*- coding: utf-8 -*-
import os 
import csv
import time 
import pandas as pd 
from pandas import DataFrame
from bs4 import BeautifulSoup, NavigableString
from libs.logging_process import Logging_process
from libs.selenium_process import Selenium_process

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

logger = Logging_process("crawler_selenium")

class Crawler_BS4(object):
    """crawler 부분"""

    def __init__(self, driver):
        """driver를 받아 BeautifulSoup 객체를 생성한다."""

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

        save_path = os.path.join("data", 'html_file')
        try:
            os.mkdir(save_path)
        except:
            pass

        save_file_path = os.path.join(save_path, 'html_file.txt')

        with open(save_file_path, "w", encoding = "utf-8") as f:

            for line in soup:

                f.write(str(line) + '\n')


    def data_to_df(self, df):
        """soup의 data 들을 DataFrame 으로 추가함"""
 
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

                        # temp 가 class="first" 이고 scope="col" 일때 
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

                            # 보통 여기서 처리 
                            if scope == 'row':

                                if j % 2 == 0:
                                    temp_column_name = temp.get_text().strip()
                                elif j % 2 == 1:
                                    if temp_column_name in df.columns:
                                        df.at[num, temp_column_name] = temp.get_text().strip()
                                    else:
                                        pass

                            # "유통가능주식수" 부분을 처리하기 위함 
                            else:
                                if j < 2:
                                    # 각 항목명과 "보통주" 를 넣기 
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


                        # 발행주식수 부분 처리
                        elif rowspan_num == 2:
                            if row_count == rowspan_num:
                                # '발행주식수', '공모전 (주)', '공모전 (후)' 를 넣기 
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

                        # 4 -> 공모금액 처리
                        # 6 -> 그룹별배정 처리
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
                                    # 항목명 넣기 
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
                    # 한 <tr> 태그 안 부분이 끝날때마다  
                    row_count -= 1 

            print(df) 
        
        except Exception as error:
            logger.info(error)
            return df 

        logger.info("row 추가 완료")
        return df          


class Crawler_Selenium(object):

    def __init__(self, url):

        self.sp = Selenium_process(url)

    def input_day(self, driver, click_id, day):
        """청구일 기간 날짜를 입력하는 부분"""
        logger.info("click_id : {} ".format(click_id))
        logger.info("day {} ".format(day))

        try:
            find_id = self.sp.find_by_id(driver, click_id)
            find_id.clear()
            find_id.send_keys(day)
            time.sleep(2)
            find_id.send_keys(Keys.ENTER)
        except Exception as error:
            logger.info(error)
            self.sp.down_chromedriver(driver)


    def click_popup_list(self, driver, _list, df):
        """popup 부분을 click 하여 main_page를 교체한 후 Crawler_BS4로 driver를 보낸다."""

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
        driver = self.sp.run_chromedriver()
        driver.implicitly_wait(5)
        self.main_page = driver.current_window_handle
        #time.sleep(3)

        #검색 시작 날짜 
        click_id = 'fromDate'
        day = '20201101'
        self.input_day(driver, click_id, day)

        #time.sleep(2)

        #검색 종료 날짜
        click_id = 'toDate'
        day = '20210101'
        self.input_day(driver, click_id, day)

        #time.sleep(2)

        #검색 누르기 
        class_name = 'btn-sprite.type-00.vmiddle.search-btn'
        search = self.sp.find_by_class(driver, class_name)
        search.click()
        #time.sleep(3)

        #전체 페이지 갯수 가져오기 
        #나중에 페이지를 넘기기 위해서 가져옴
        cbs4 = Crawler_BS4(driver)
        #time.sleep(3)
        index_num, all_index_num = cbs4.find_index()
        logger.info("index_num : {} ".format(index_num))
        logger.info("all_index_num : {}".format(all_index_num))

        click_css = 'td.first'

        list_by_css = self.sp.find_list_by_css(driver, click_css)
        #time.sleep(3)

        df = self.click_popup_list(driver, list_by_css, df)
        #time.sleep(3)

        next_page_xpath = '//*[@id="main-contents"]/section[2]/div[1]/a[{}]'.format(all_index_num + 3)

        while(index_num < all_index_num):
            
            index_num += 1
            next_page = driver.find_element_by_xpath(next_page_xpath)
            logger.info("index_num : {} ".format(index_num))
            
            next_page.click()
            #time.sleep(3)

            self.main_page = driver.current_window_handle
            #time.sleep(3)

            click_css = 'td.first'

            list_by_css = self.sp.find_list_by_css(driver, click_css)
            #time.sleep(3)

            df = self.click_popup_list(driver, list_by_css, df)
            #time.sleep(3)

            
        print(df)

        df.to_csv(os.path.join("data", "csv_file", save_csv))

        self.sp.down_chromedriver(driver)

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