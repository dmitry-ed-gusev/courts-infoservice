"""scrap js page of len obl sud"""

import threading
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pymysql
from bs4 import BeautifulSoup
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from court_cases_scraper.src.courts.db import db_tools
from court_cases_scraper.src.courts.common import misc
from court_cases_scraper.src.courts.config import scraper_config as config

# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def parse_page_6(court: dict, check_date: str) -> list[dict[str, str]]:
    """parses output js page"""
    result = []
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1024")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")
    options.add_argument("--user-agent " + config.USER_AGENT)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    logger.debug(f"Date {check_date}")
    driver.get(
        court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get("server_num") + "&H_date=" + check_date)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("div", id="tablcont")
    # <div id="resultTable">
    for table in tables:
        section_name = ""
        sections = table.find_all("tr")
        # tr
        for idx, section in enumerate(sections):
            if idx == 0:
                continue
            # setting new section
            if len(section.find_all("td")) == 1:
                for idx_r, row in enumerate(section.find_all("td")):
                    section_name = row.text.title()
            # appending row
            else:
                result_row = {"section_name": section_name}
                # td
                for idx_r, row in enumerate(section.find_all("td")):
                    if row.text:
                        result_row["col" + str(idx_r)] = row.text.replace("БЕЗ ИМЕНИ!", "").strip()
                    else:
                        result_row["col" + str(idx_r)] = str(row.contents).strip()
                    if row.find(href=True):
                        result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result_row["court_alias"] = court.get("alias")
                result.append(result_row)
    return result


def parser_type_6(court: dict[str, str], db_config: dict[str, str]) -> None:
    """Парсер тип 3"""
    result_len = 0
    futures = []  # list to store future results of threads
    db_tools.clean_stage_table(db_config)
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_6) as executor:
        for date in misc.daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                                   datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            future = executor.submit(parse_page_6, court, check_date)
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
