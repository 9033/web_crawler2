import pandas as pd 
from pandas import DataFrame

from naver_finance.doller import Naver_finance_crawler

url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW"

df = DataFrame(columns = ['매매기준율'])

nfc = Naver_finance_crawler(url, df)
save_csv = 'doller.csv'
#last_scrap_day = 
nfc.run(save_csv)