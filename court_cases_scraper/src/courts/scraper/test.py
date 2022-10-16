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
                                                    parser_7,
                                                    parser_8)

test_mode = 8
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
    case 1:
        court = {"title": "Василеостровский районный суд", "link": "https://vos--spb.sudrf.ru", "server_num": "1", "alias": "spb-vos",
                 "check_date": check_date_dt}
        result, out_court, status = parser_1.parse_page(court)
    case 3:
        court = {"title": "KRD_KKS", "link": "https://kraevoi--krd.sudrf.ru", "server_num": "1", "alias": "krd-kks",
                 "check_date": check_date_dt}
        result, out_court, status = parser_3.parse_page(court)
    case 7:
        court = {"title": "stav mir sud", "link": "https://stavmirsud.ru/officework", "alias": "stav-mir",
                 "check_date": check_date_dt}
        result, out_court, status = parser_7.parse_page(court)
    case 8:
        court = {"title": "arbitr stav", "link": "https://rad.arbitr.ru", "alias": "stav-arbitr",
                 "server_num": "MSK", "check_date": check_date_dt}
        result, out_court, status = parser_8.parse_page(court)
    case _:
        result = []
        status = ""
        out_court = []
db_tools.load_to_stage_alchemy(result, db_config)

print(result)
print(len(result))
