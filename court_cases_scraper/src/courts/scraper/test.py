"""
script for debugging
don't include in setup
"""
from datetime import datetime
import os
from dotenv import load_dotenv
from loguru import logger
from court_cases_scraper.src.courts.db import db_tools
from court_cases_scraper.src.courts.scraper import (parser_1,
                                                    parser_2,
                                                    parser_3,
                                                    parser_4,
                                                    parser_5,
                                                    parser_6,
                                                    parser_7)

test_mode = 7
check_date = "10.10.2022"
check_date_dt = datetime.strptime("10.10.2022", "%d.%m.%Y")

# Load environment variables from .env file from the project root dir
load_dotenv()
db_config = {"host": os.environ["MYSQL_HOST"],
             "port": os.environ["MYSQL_PORT"],
             "user": os.environ["MYSQL_USER"],
             "passwd": os.environ["MYSQL_PASS"],
             "db": os.environ["MYSQL_DB"]}

match test_mode:
    case 3:
        court = {"title": "KRD_KKS", "link": "https://kraevoi--krd.sudrf.ru", "server_num": "1", "alias": "krd-kks"}
        result = parser_3.parse_page_3(court, check_date)
    case 7:
        court = {"title": "stav mir sud", "link": "https://stavmirsud.ru/officework", "alias": "stav-mir"}
        case_type = "caselistcs"

        result = parser_7.parse_page_7(court, check_date_dt, case_type)
    case _:
        result = []

print(result)
print(len(result))
