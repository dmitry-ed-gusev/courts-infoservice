"""scrap moscow mir courts"""
import time
from datetime import datetime, timedelta

import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import pymysql
from bs4 import BeautifulSoup
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from court_cases_scraper.src.courts.db import db_tools
from court_cases_scraper.src.courts.common import misc
from court_cases_scraper.src.courts.config import scraper_config as config

# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def parse_page_5(court: dict, check_date: str) -> list[dict[str, str]]:
    """parses mos sud page with paging"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1024")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    result = []
    page_num = 1
    pages_total = 1
    order_num = 0
    while True:
        driver.get(court.get(
            "link") + "/hearing?hearingRangeDateFrom=" + check_date + "&hearingRangeDateTo=" + check_date + "&page=" + str(
            page_num))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all("div", class_="wrapper-search-tables")
        # <div class="wrapper-search-tables">
        for table in tables:
            sections = table.find_all("tr")
            # tr
            for idx, section in enumerate(sections):
                # skip header
                if idx == 0:
                    continue
                # appending row
                else:
                    result_row = {}
                    order_num += 1
                    # td
                    for idx_r, row in enumerate(section.find_all("td")):
                        if idx_r == 2:
                            result_row["hearing_time"] = row.text.strip()[10:].strip()
                        else:
                            value = row.text.strip().replace("\n", " ").replace("\t", " ")
                            value = re.sub("\s+", " ", value)[:10000]
                            result_row["col" + str(idx_r)] = value
                            if row.find(href=True):
                                result_row["col" + str(idx_r) + "_link"] = "https://mos-sud.ru" + row.find(href=True)[
                                    "href"]

                    result_row["check_date"] = check_date
                    result_row["court"] = court.get("title")
                    result_row["court_alias"] = court.get("alias")
                    result_row["order_num"] = order_num
                    result.append(result_row)
        if page_num == 1:
            try:
                pages_total = int(soup.find("input", id="paginationFormMaxPages").attrs["value"])
            except:
                None
        logger.debug(driver.current_url + ", pages " + str(pages_total))
        if page_num < pages_total:
            page_num += 1
        else:
            break

    return result


def parser_type_5(court: dict[str, str], db_config: dict[str, str]) -> None:
    """parser for mos gor sud"""
    result_len = 0
    futures = []  # list to store future results of threads
    db_tools.clean_stage_table(db_config)
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_5) as executor:
        for date in misc.daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                                   datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            future = executor.submit(parse_page_5, court, check_date)
            futures.append(future)

            for task in as_completed(futures):
                result_part = task.result()
                result_len += len(result_part)
                db_tools.load_to_stage(result_part, config.STAGE_MAPPING_1, db_config)

    if result_len > 0:
        db_tools.load_to_dm(db_config)
        logger.info("Court " + court.get("alias") + " loaded. Total records " + str(result_len))

        conn = pymysql.connect(host=db_config.get("host"),
                               port=int(db_config.get("port")),
                               user=db_config.get("user"),
                               passwd=db_config.get("passwd"),
                               database=db_config.get("db"),
                               )

        logger.debug("Connected")
        cursor = conn.cursor()
        sql = "insert into dm_court_cases_scrap_log (court, load_dttm) values ('" + court.get("alias") + "', now())"
        cursor.execute(sql)
        conn.commit()
