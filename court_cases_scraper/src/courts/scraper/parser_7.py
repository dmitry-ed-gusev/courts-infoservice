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


def parse_page_7(court: dict, check_date: datetime, case_type: str) -> list[dict[str, str]]:
    """parses output page"""
    session = requests.Session()
    session.headers = {"user-agent": config.USER_AGENT}
    logger.debug("Date " + check_date.strftime("%d-%m-%Y"))
    result = []
    empty_flag = False
    while not empty_flag:
        page_num = 8
        order_num = 1
        retries = 0
        address = court.get("link") + "/" + case_type + "?sf5=" + check_date.strftime(
            "%Y-%m-%d") + "&sf5_d=" + check_date.strftime("%Y-%m-%d") + "&pn=" + str(page_num)
        while True:
            time.sleep(2)
            page = session.get(address)
            retries += 1
            if retries > config.MAX_RETRIES or page.status_code == 200:
                break
        soup = BeautifulSoup(page.content, 'html.parser')
        tables = soup.find_all("table", class_="decision_table")
        # <table class=decision_table>
        for table in tables:
            sections = table.find_all("tr")
            if len(sections) == 2:
                empty_flag = True
                break
            # tr
            for idx, section in enumerate(sections):
                # skip header
                if idx == 0:
                    continue
                # appending row
                else:
                    result_row = {}
                    # td
                    for idx_r, row in enumerate(section.find_all("td")):
                        if idx_r == 0:
                            continue
                        if row.text:
                            result_row["col" + str(idx_r)] = row.text.strip()
                        else:
                            result_row["col" + str(idx_r)] = str(row.contents).strip()
                        if row.find(href=True):
                            result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]
                    match case_type:
                        case "caselistcs":
                            result_row["section_name"] = "Гражданские дела"

                            if result_row.get("col4"):
                                result_row["case_info"] = "Истец: " + result_row.get("col4")
                            else:
                                result_row["case_info"] = ""
                            if result_row.get("col5"):
                                result_row["case_info"] = ". Ответчик: " + result_row.get("col5")
                            if result_row.get("col6"):
                                result_row["case_info"] = ". Категория: " + result_row.get("col6")
                        case "caselistus":
                            result_row["section_name"] = "Уголовные дела"
                        case "caselistas":
                            result_row["section_name"] = "Дела об административных правонарушениях"
                    result_row["court"] = "Мировой суд " + result_row.get("col1") + ", участок " + result_row.get(
                        "col2")
                    result_row["check_date"] = check_date.strftime("%d.%m.%Y")
                    result_row["court_alias"] = court.get("alias")
                    result_row["order_num"] = str(order_num)
                    order_num += 1
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
            for case_type in case_types:
                future = executor.submit(parse_page_7, court, date, case_type)
                futures.append(future)

        for task in as_completed(futures):
            result_part = task.result()
            result_len += len(result_part)
            db_tools.load_to_stage(result_part, config.STAGE_MAPPING_7, db_config)

    if result_len > 0:
        db_tools.load_to_dm(db_config)
        logger.info("Court " + court.get("alias") + " loaded. Total records " + str(result_len))
        db_tools.log_scrapped_court(db_config, court.get("alias"))
