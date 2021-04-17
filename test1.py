# -*- coding: utf-8 -*-
import os 
import time 
from selenium import webdriver

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Selenium_Test(object):

    def __init__(self):

        self.url = "http://naver.com"

        self.chromedriver_path = os.path.join(BASE_DIR, "chromedriver_win32", "chromedriver.exe")
        self.save_screenshot_path = os.path.join(BASE_DIR, "data", "naver20210317.png")

    def run_chromedriver(self, chromedriver_path):

        driver = webdriver.Chrome(chromedriver_path)
        driver.get(self.url)

        return driver
    
    def save_screenshot(self, driver, save_screenshot_path):

        file_path, _ = os.path.split(save_screenshot_path)

        if not os.path.isdir(file_path):
            os.mkdir(file_path)

        driver.save_screenshot(save_screenshot_path)
    
    def down_chromedriver(self, driver):

        driver.quit()

    def run(self):

        driver = self.run_chromedriver(self.chromedriver_path)

        time.sleep(5)

        self.save_screenshot(driver, self.save_screenshot_path)

        time.sleep(5)

        self.down_chromedriver(driver)

if __name__ == "__main__":
    selenium_test = Selenium_Test()

    selenium_test.run()