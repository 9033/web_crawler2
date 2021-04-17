import logging
import pandas as pd 
from pandas import DataFrame
from bs4 import BeautifulSoup, NavigableString

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

class InvstgCorp_Test(object):

    def __init__(self):

        self.html = self.load_html()

        self.soup = BeautifulSoup(self.html, "html.parser")

    def load_html(self):

        load_html_txt = ""

        load_path = "html_save\\html_file.txt"

        with open(load_path, 'r', encoding = 'utf-8') as f:

            lines = f.readlines()

            for line in lines:
                
                load_html_txt += line
                load_html_txt += '\n'
            

        return load_html_txt


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
                                    print(temp_list)
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

                                temp_list.append(temp.get_text().strip())

                            else:
                                print(temp_list)
                                temp_join_list = [temp_list[0], temp_list[j+1]]
                                temp_column_name = '-'.join(temp_join_list)
                                if temp_column_name in df.columns:
                                    df.at[num, temp_column_name] = temp.get_text().strip()
                                else:
                                    pass

                        elif rowspan_num in [4,6]:
                            if row_count == rowspan_num:
                                if j in [0,2]:
                                    # "공모금액" 그리고 "주식수 (주)" 넣기 
                                    temp_list.append(temp.get_text().strip())
                                else:
                                    pass

                            else:
                                if j == 0:

                                    temp_list.append(temp.get_text().strip())

                                elif j == 1:
                                    print(temp_list)
                                    temp_join_list = [temp_list[0], temp_list[1], temp_list[(rowspan_num + 1)-row_count]]
                                    temp_column_name = '-'.join(temp_join_list)
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
        
        except AttributeError as error:
            logger.info(error)
        

        return df    


    def run(self):

        # df = DataFrame(columns = ['회사명', '심사청구일', '심사결과', '신규상장', '업종', '기업구분', '결산월', '상장(예정)주식수', '공모(예정)주식수', '상장주선인'])
        df = DataFrame(columns = ['회사명', '설립일', '업종', '결산월', '기업구분',\
             '수요예측일정', '공모청약일정', '상장(예정)일', '납입일', '희망공모가격',\
             '발행주식수-공모전 (주)', '발행주식수-공모후 (주)',\
             '공모금액-주식수 (주)-모집', '공모금액-주식수 (주)-매출', '공모금액-주식수 (주)-총액',\
             '그룹별배정-주식수 (주)-우리사주조합', '그룹별배정-주식수 (주)-기관투자자', '그룹별배정-주식수 (주)-일반투자자', '그룹별배정-주식수 (주)-기타', '그룹별배정-주식수 (주)-합계',\
             '사모(주관사인수)-주식수',\
             '상장주식수-보통주', '의무보유-보통주', '우리사주-보통주', '유통가능주식수-보통주'])

        df = self.PubofrProgCom(df)

        df.to_csv("simple_test2.csv")

if __name__ == "__main__":
    ic = InvstgCorp_Test()
    ic.run()