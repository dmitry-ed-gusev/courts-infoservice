"""scrap stav mir sud"""
from datetime import datetime, timedelta
import time
import threading
import requests
from bs4 import BeautifulSoup
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from court_cases_scraper.src.courts.db import db_tools
from court_cases_scraper.src.courts.common import misc
from court_cases_scraper.src.courts.config import scraper_config as config

# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def parse_page_7(court: dict, check_date: str) -> list[dict[str, str]]:
    """parses output page"""
    session = requests.Session()
    session.headers = {"user-agent": config.USER_AGENT}
    logger.debug(f"Date {check_date}")
    retries = 0
    page = session.get(court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get(
        "server_num") + "&H_date=" + check_date)
    while page.status_code != 200:
        time.sleep(2)
        page = session.get(court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get(
            "server_num") + "&H_date=" + check_date)
        retries += 1
        if retries > config.MAX_RETRIES:
            break
    result = []
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("div", id="tablcont")
    # <div id="tablcont">
    for table in tables:
        section_name = ""
        sections = table.find_all("tr")
        # tr
        for idx, section in enumerate(sections):
            if idx == 0:
                continue
            # setting new section
            if len(section.contents) == 1:
                for idx_r, row in enumerate(section.find_all("td")):
                    section_name = row.text
            # appending row
            else:
                result_row = {"section_name": section_name}
                # td
                for idx_r, row in enumerate(section.find_all("td")):
                    if row.text:
                        result_row["col" + str(idx_r)] = row.text.strip()
                    else:
                        result_row["col" + str(idx_r)] = str(row.contents).strip()
                    if row.find(href=True):
                        result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result_row["court_alias"] = court.get("alias")
                result.append(result_row)
    return result


def parser_type_7(court: dict[str, str], db_config: dict[str, str]) -> None:
    """Парсер тип 7"""
    result_len = 0
    futures = []  # list to store future results of threads
    db_tools.clean_stage_table(db_config)
    case_types = ["caselistcs", "caselistus", "caselistas"]
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_7) as executor:
        for date in misc.daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                                   datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            future = executor.submit(parse_page_7, court, check_date)
            futures.append(future)

        for task in as_completed(futures):
            result_part = task.result()
            result_len += len(result_part)
            db_tools.load_to_stage(result_part, config.STAGE_MAPPING_7, db_config)

    if result_len > 0:
        db_tools.load_to_dm(db_config)
        logger.info("Court " + court.get("alias") + " loaded. Total records " + str(result_len))
        db_tools.log_scrapped_court(db_config, court.get("alias"))
