"""
script for debugging
don't include in setup
"""

import os
from dotenv import load_dotenv
from loguru import logger
from court_cases_scraper.src.courts.db import db_tools
from court_cases_scraper.src.courts.scraper import parser_1, parser_2, parser_3, parser_4, parser_5, parser_6


# Load environment variables from .env file from the project root dir
load_dotenv()
db_config = {"host": os.environ["MYSQL_HOST"],
             "port": os.environ["MYSQL_PORT"],
             "user": os.environ["MYSQL_USER"],
             "passwd": os.environ["MYSQL_PASS"],
             "db": os.environ["MYSQL_DB"]}

court = {"title": "https://mirsud.spb.ru", "link": "https://mirsud.spb.ru", "server_num": "1"}
check_date = "10.10.2022"
result = parser_4.parse_page_4(court, check_date)

print(result)
print(len(result))
