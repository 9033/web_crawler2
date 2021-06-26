import naver_finance_ver2.scrap_all

from libs.logging_process import Logging_process

logger = Logging_process('qubot_test')

logger.info("qubot_test start")

scrapper = naver_finance_ver2.scrap_all.scrap_all()

try:
    scrapper.scrap_check()

    logger.info("qubot_test end")

except Exception as error:
    logger.info("qubot_test error !! : {}".format(error))
    
