import pandas as pd 
from pandas import DataFrame
from kind_krx.InvstgCorp_test import InvstgCorp_Test
from kind_krx.crawler_selenium import Crawler_Selenium

# invst = InvstgCorp_Test()

# invst.run()

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