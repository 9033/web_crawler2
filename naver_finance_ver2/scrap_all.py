import json
from libs.logging_process import Logging_process

from naver_finance_ver2 import scrap_macro_economics_test as sme

logger = Logging_process('scrap_all')

class scrap_all(object):

    def __init__(self):

        self.sme = sme.scrap_macro_economics()

    def read_config_json(self):
        "(name, url, page) 가 저장된 json 파일을 읽어들임"

        config_json_path = './setting_files/macro_economics_config.json'

        try:
            config_f = open(config_json_path,encoding = "utf-8")
            logger.info("macro_economics_config.json 읽어들임")
        except Exception as error:
            logger.info(error)
            return None

        config_f_data = json.load(config_f)

        config_f.close()

        return config_f_data

    def scrap_check(self):
        '''스크랩 실행'''

        # sql = """SELECT * FROM status.scrap_all_status"""
        # self.cur.execute(sql)
        # checklist = self.cur.fetchall()
        # checklist = list(checklist[0].values())
        # 
        # if checklist[2] != self.today:
        #     self.logger.info("macro_economics 스크랩 시작!")
        #     # macro_economics 스크랩 실행
        #     self.sme.scrap_macro_economics()
        #     sql = f"UPDATE status.scrap_all_status SET macro_economics_scraped='20200101'"    # '{self.today}'"
        #     self.cur.execute(sql)
        #     self.conn.commit()
        #     self.logger.info("macro_economics 스크랩 완료!")      

        config_f_data = self.read_config_json()

        # print(config_f_data)

        # exchange_rate_index = config_f_data['exchange_rate_index']

        # for index in exchange_rate_index:

        #     name = index['name']
        #     url = index['url']
        #     page = index['page']

        #     if page == 0:
        #         pass
        #     else:
        #         self.sme.scrap_exchange_rate(name, url, page)

        # interest_rate_index = config_f_data['interest_rate_index']

        # for index in interest_rate_index:

        #     name = index['name']
        #     url = index['url']
        #     page = index['page']

        #     if page == 0:
        #         pass
        #     else:
        #         self.sme.scrap_interest_rate(name, url, page)

        # gold_oil_index = config_f_data['gold_oil_index']

        # for index in gold_oil_index:

        #     name = index['name']
        #     url = index['url']
        #     page = index['page']

        #     if page == 0:
        #         pass
        #     else:
        #         self.sme.scrap_gold_oil(name, url, page)

        # non_ferrous_metal_index = config_f_data['non_ferrous_metal_index']

        # for index in non_ferrous_metal_index:

        #     name = index['name']
        #     url = index['url']
        #     page = index['page']

        #     if page == 0:
        #         pass
        #     else:
        #         self.sme.scrap_non_ferrous_metal(name, url, page)

        # agricultural_product_index = config_f_data['agricultural_product_index']

        # for index in agricultural_product_index:

        #     name = index['name']
        #     url = index['url']
        #     page = index['page']

        #     if page == 0:
        #         pass
        #     else:
        #         self.sme.scrap_agricultural_product(name, url, page)

        # # stock 은 Selenium 이 필요함

        stock_index = config_f_data['stock_index']

        for stock in stock_index:

            name = stock['name']
            url = stock['url']
            page = stock['page']

            if page == 0:
                pass
            else:
                self.sme.scrap_global_stock(name, url, page)


