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
    case 3:
        court = {"title": "KRD_KKS", "link": "https://kraevoi--krd.sudrf.ru", "server_num": "1", "alias": "krd-kks",
                 "check_date": check_date_dt}
        result, out_court, mapping = parser_3.parse_page(court)
    case 7:
        court = {"title": "stav mir sud", "link": "https://stavmirsud.ru/officework", "alias": "stav-mir",
                 "check_date": check_date_dt}
        result, out_court, mapping = parser_7.parse_page(court)
    case 8:
        cookies = "__ddg1_=oTAQC2DvxbRzMdNU2icQ; ASP.NET_SessionId=p4mt4tkanxn5pntfhczzeduo; CUID=c8c41558-b404-47f4-9d6d-df9e92eaa113:bYmkaXqbP5ft9GkJAAft1A==; pr_fp=20466da67c98adee4e3f6289d94f10a2b15d1c3cd17eec73e3efdb1aeb82edbd; rcid=d9d9ca28-eee3-4d6a-a9e5-13aeba522ce7; wasm=9a4a226a1e6f3d9a4f4e23c9dc41f3c8"
        court = {"title": "arbitr stav", "link": "https://rad.arbitr.ru", "alias": "stav-arbitr",
                 "server_num": "MSK", "check_date": check_date_dt}
        result, out_court, mapping = parser_8.parse_page(court, cookies)
    case _:
        result = []
        mapping = []
        out_court = []

print(result)
print(len(result))
