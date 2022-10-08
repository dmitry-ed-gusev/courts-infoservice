"""scrap spb miroviye sudy"""
import time
import threading
from datetime import datetime, timedelta

import pymysql
import requests
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from court_cases_scraper.src.courts.db import db_tools
from court_cases_scraper.src.courts.common import misc
from court_cases_scraper.src.courts.config import scraper_config as config

# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def parse_page_4(court: dict, check_date: str, case_type: str) -> list[dict[str, str]]:
    """parses output page"""
    session = requests.Session()
    result = []
    order_num = 0
    page_num = 1
    logger.debug(f"Date {check_date}, case type {case_type}")
    while True:
        content_json = None
        while True:
            api_search = court.get("link") + \
                         "/cases/api/search/?adm_person_type=all&article=&civil_person_type=" + \
                         "all&court_number=&criminal_person_type=all&date_from=" + check_date + \
                         "&date_to=" + check_date + "&full_name=&id=&page=" + str(page_num) + "&type=" + case_type
            get_search = session.get(api_search)
            if get_search.status_code == 200:
                break
            else:
                time.sleep(2)

        search_id = get_search.json()["id"]
        finished = False
        total_tries = 0
        while not finished:
            total_tries += 1
            content = session.get(court.get("link") + "/cases/api/results/?id=" + search_id)
            if content.status_code == 200:
                content_json = content.json()
                finished = content_json["finished"]
            if not finished:
                time.sleep(2)
            if total_tries > config.MAX_RETRIES:
                break

        for row in content_json["result"]["data"]:
            order_num += 1
            case_info = None
            if case_type == "adm":
                if row.get("offenders"):
                    case_info = "Лицо, в отношении которого ведется производство по делу об административном правонарушении: " + \
                                row.get("offenders")
                    if row.get("article"):
                        case_info = case_info + ". Статья КоАП РФ " + row.get("article")
                section_name = "Дела об АП"
            elif case_type == "criminal":
                if row.get("defendants"):
                    case_info = "Подсудимый: " + row.get("defendants")
                    if row.get("article"):
                        case_info = case_info + ". Статья УК РФ " + row.get("article")
                section_name = "Уголовные дела"
            else:
                if case_type == "civil":
                    section_name = "Гражданские дела"
                else:
                    section_name = "Административные дела"
                case_info = None
                if row.get("claimants"):
                    case_info = "Истец: " + row.get("claimants")
                    if row.get("respondents"):
                        case_info = case_info + ". Ответчик: " + row.get("respondents")
                    if row.get("third_parties"):
                        case_info = case_info + ". Третьия лица: " + row.get("third_parties")

            result.append({"case_num": row.get("id"),
                           "case_link": court.get("link") + row.get("url"),
                           "court": court.get("title") + " Участок " + row.get("court_number"),
                           "check_date": check_date,
                           "status": row.get("status"),
                           "order_num": order_num,
                           "case_info": case_info,
                           "section_name": section_name
                           })

        if len(content_json['result']['data']) == 0:
            break
        else:
            page_num += 1

    logger.debug(f"Date {check_date} case type {case_type} finished")
    return result


def parser_type_4(court: dict[str, str], db_config: dict[str, str]) -> None:
    """Парсер тип 4"""
    result = []
    futures = []  # list to store future results of threads
    case_types = ["adm", "civil", "criminal", "public"]
    db_tools.clean_stage_table(db_config)
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_4) as executor:
        for date in misc.daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                              datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            for case_type in case_types:
                future = executor.submit(parse_page_4, court, check_date, case_type)
                futures.append(future)

        for task in as_completed(futures):
            result_part = task.result()
            result.extend(result_part)

    if len(result) > 0:
        logger.debug("Connecting to db")

        conn = pymysql.connect(host=db_config.get("host"),
                               port=int(db_config.get("port")),
                               user=db_config.get("user"),
                               passwd=db_config.get("passwd")
                               )

        logger.debug("Connected")
        cursor = conn.cursor()
        db_tools.load_to_stage(result, config.STAGE_MAPPING_4, db_config)
        db_tools.load_to_dm(db_config)
        sql = "insert into dm.court_cases_scrap_log (court, load_dttm) values ('" + court.get("alias") + "', now())"
        cursor.execute(sql)
        conn.commit()
