# -*- coding: utf-8 -*-
import os 
import time 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Selenium_Test(object):

    def __init__(self, url):

        self.url = url
        self.chromedriver_path = os.path.join(BASE_DIR, "chromedriver_win32", "chromedriver.exe")

    def run_chromedriver(self, chromedriver_path):

        driver = webdriver.Chrome(chromedriver_path)
        driver.get(self.url)

        return driver  

    def find_list_by_id(self, driver, click_id):

        list_by_id = driver.find_elements_by_id(click_id)

        return list_by_id

    def down_chromedriver(self, driver):

        driver.quit() 

    def click_popup_list(self, driver, _list):

        i = 0

        for i in range(len(_list)):

            _list[i].click()

            for handle in driver.window_handles:
                if handle != self.main_page:
                    new_page = handle

            driver.switch_to.window(new_page)

            time.sleep(3)

            self.test_print(driver)

            time.sleep(3)

            driver.close()

            driver.switch_to.window(self.main_page)

            i += 1


            if i > 2:
                break

    def test_print(self, driver):
        print("test_print")

        html = driver.page_source
        #print(html)
        soup = BeautifulSoup(html, "html.parser")
        #print(soup)

        td_list = soup.find_all('td')

        for td in td_list:
            print(td.get_text().strip())



    def run(self):

        driver = self.run_chromedriver(self.chromedriver_path)
        self.main_page = driver.current_window_handle
        time.sleep(3)

        click_id = "companysum"

        list_by_id = self.find_list_by_id(driver, click_id)
        time.sleep(3)

        self.click_popup_list(driver, list_by_id)

        self.down_chromedriver(driver)




if __name__ == "__main__":

    url = "https://kind.krx.co.kr/disclosure/todaydisclosure.do?method=searchTodayDisclosureMain&marketType=0"

    selenium_test = Selenium_Test(url)

    selenium_test.run()
            