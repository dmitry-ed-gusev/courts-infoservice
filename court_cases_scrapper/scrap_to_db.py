"""
parse court data and load to stage
"""
import time
import re
import threading
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pymysql
import requests
from bs4 import BeautifulSoup
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from court_cases_scrapper import config

logger.debug("Connecting to db")

conn = pymysql.connect(host=config.MYSQL_CONNECT["host"],
                       port=config.MYSQL_CONNECT["port"],
                       user=config.MYSQL_CONNECT["user"],
                       passwd=config.MYSQL_CONNECT["passwd"]
                       )

logger.debug("Connected")
cursor = conn.cursor()

# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def calculate_row_hash_stage():
    """calcs row hash in stage"""
    sql = "call stage.p_update_court_cases_row_hash()"
    cursor.execute(sql)
    conn.commit()


def load_to_dm():
    """calls load to dm procedure"""
    sql = "call dm.p_load_court_cases()"
    cursor.execute(sql)
    conn.commit()


def read_courts_config() -> list[dict[str, str]]:
    result = []
    cursor.execute("""
            with max_load_date as (
            select court, max(load_dttm) as load_dttm from dm.court_cases_scrap_log group by court
            )
            select cfg.link, cfg.title, cfg.alias, cfg.server_num, cfg.parser_type
            from dm.court_scrap_config cfg
                left join max_load_date log
            	    on cfg.alias = log.court
            where not skip
            	and (log.court is null or date_add(now(), interval -23 hour) > log.load_dttm)
            """)
    result_1 = cursor.fetchall()
    if result_1:
        for row1 in result_1:
            result.append(
                {"link": row1[0],
                 "title": row1[1],
                 "alias": row1[2],
                 "server_num": row1[3],
                 "parser_type": row1[4]}
            )

    return result


def clean_stage_table():
    """clean stage table"""
    logger.debug("Cleaning stage table " + config.STAGE_TABLE)
    sql = "delete from " + config.STAGE_TABLE
    cursor.execute(sql)
    logger.debug("Stage table cleaned")
    conn.commit()


def load_to_stage(data: list[dict[str, str]], stage_mapping: list[dict[str, str]]) -> None:
    """loads parsed data to stage"""
    sql_part1 = f"INSERT INTO {config.STAGE_TABLE} ("
    sql_part2 = ""

    for field in stage_mapping:
        sql_part1 = sql_part1 + field.get("name") + ", "
        if field.get("constant"):
            sql_part2 = sql_part2 + field.get("constant") + ", "
        else:
            sql_part2 = sql_part2 + "%s, "

    sql_statement = sql_part1.rstrip(", ") + ") VALUES (" + sql_part2.rstrip(", ") + ")"

    logger.debug(sql_statement)

    logger.debug("Stage data load start")
    for idx_r, row in enumerate(data):
        values = []
        for idx_c, col in enumerate(stage_mapping):
            if row.get(col.get("mapping")):
                values.append(row.get(col.get("mapping")))
            elif col.get("mapping"):
                values.append(None)
        cursor.execute(sql_statement, values)
        if idx_r % config.COMMIT_INTERVAL == 0 and idx_r > 0:
            conn.commit()
            logger.debug("Commit " + str(idx_r))
    conn.commit()
    cursor.execute("call stage.p_update_court_cases_row_hash()")
    conn.commit()
    logger.debug("Stage data load completed")


def daterange(date1: datetime, date2: datetime) -> list[datetime]:
    result = []
    for n in range(int((date2 - date1).days) + 1):
        result.append((date1 + timedelta(days=n)))

    return result


def parse_page_1(court: dict, check_date: str) -> list[dict[str, str]]:
    """parses output page"""
    session = requests.Session()
    session.headers = {"user-agent": config.USER_AGENT}
    logger.debug(f"Date {check_date}")
    page = session.get(court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get(
        "server_num") + "&H_date=" + check_date)
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
                result.append(result_row)
    return result


def parser_type_1(court: dict[str, str]) -> None:
    """Парсер тип 1"""
    result = []
    futures = []  # list to store future results of threads
    clean_stage_table()
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_1) as executor:
        for date in daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                              datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            future = executor.submit(parse_page_1, court, check_date)
            futures.append(future)

        for task in as_completed(futures):
            result_part = task.result()
            result.extend(result_part)

    if len(result) > 0:
        load_to_stage(result, config.STAGE_MAPPING_1)
        load_to_dm()
        sql = "insert into dm.court_cases_scrap_log (court, load_dttm) values ('" + court.get("alias") + "', now())"
        cursor.execute(sql)
        conn.commit()


def parse_page_2(court: dict, check_date: str) -> list[dict[str, str]]:
    """parses mos gor sud page with paging"""
    session = requests.Session()
    session.headers = {"user-agent": config.USER_AGENT}
    result = []
    page_num = 1
    pages_total = 1
    order_num = 0
    while True:
        page = session.get(
            court.get("link") +
            "&hearingRangeDateFrom=" + check_date +
            "&hearingRangeDateTo=" + check_date +
            "&page=" + str(page_num)
        )
        soup = BeautifulSoup(page.content, 'html.parser')
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
                        if idx_r == 3:
                            result_row["hearing_time"] = row.text.strip()[10:].strip()
                        else:
                            value = row.text.strip().replace("\n", " ").replace("\t", " ")
                            value = re.sub("\s+", " ", value)[:10000]
                            result_row["col" + str(idx_r)] = value
                            if row.find(href=True):
                                result_row["col" + str(idx_r) + "_link"] = "https://mos-gorsud.ru" + \
                                                                           row.find(href=True)["href"]

                    result_row["check_date"] = check_date
                    result_row["court"] = court.get("title")
                    result_row["order_num"] = order_num
                    result.append(result_row)
        if page_num == 1:
            try:
                pages_total = int(soup.find("input", id="paginationFormMaxPages").attrs["value"])
            except:
                None
        logger.debug(str(page.url) + ", pages " + str(pages_total))
        if page_num < pages_total:
            page_num += 1
        else:
            break

    return result


def parser_type_2(court: dict[str, str]) -> None:
    """parser for mos gor sud"""
    result = []
    futures = []  # list to store future results of threads
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_2) as executor:
        for date in daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                              datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            future = executor.submit(parse_page_2, court, check_date)
            futures.append(future)

        for task in as_completed(futures):
            result_part = task.result()
            result.extend(result_part)
    if len(result) > 0:
        load_to_stage(result, config.STAGE_MAPPING_2)
        load_to_dm()
        sql = "insert into dm.court_cases_scrap_log (court, load_dttm) values ('" + court.get("alias") + "', now())"
        cursor.execute(sql)
        conn.commit()


def parse_page_3(court: dict, check_date: str) -> list[dict[str, str]]:
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
    tables = soup.find_all("div", id="resultTable")
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
                        result_row["col" + str(idx_r)] = row.text.strip()
                    else:
                        result_row["col" + str(idx_r)] = str(row.contents).strip()
                    if row.find(href=True):
                        result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result.append(result_row)
    return result


def parser_type_3(court: dict[str, str]) -> None:
    """Парсер тип 3"""
    result = []
    futures = []  # list to store future results of threads
    clean_stage_table()
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_3) as executor:
        for date in daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                              datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            future = executor.submit(parse_page_3, court, check_date)
            futures.append(future)

        for task in as_completed(futures):
            result_part = task.result()
            result.extend(result_part)

    if len(result) > 0:
        load_to_stage(result, config.STAGE_MAPPING_3)
        load_to_dm()
        sql = "insert into dm.court_cases_scrap_log (court, load_dttm) values ('" + court.get("alias") + "', now())"
        cursor.execute(sql)
        conn.commit()


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
            if total_tries > 20:
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


def parser_type_4(court: dict[str, str]) -> None:
    """Парсер тип 4"""
    result = []
    futures = []  # list to store future results of threads
    case_types = ["adm", "civil", "criminal", "public"]
    clean_stage_table()
    with ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_4) as executor:
        for date in daterange(datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                              datetime.now() + timedelta(days=config.RANGE_FORWARD)):
            check_date = date.strftime("%d.%m.%Y")
            for case_type in case_types:
                future = executor.submit(parse_page_4, court, check_date, case_type)
                futures.append(future)

        for task in as_completed(futures):
            result_part = task.result()
            result.extend(result_part)

    if len(result) > 0:
        load_to_stage(result, config.STAGE_MAPPING_4)
        load_to_dm()
        sql = "insert into dm.court_cases_scrap_log (court, load_dttm) values ('" + court.get("alias") + "', now())"
        cursor.execute(sql)
        conn.commit()


def scrap_courts(courts_config: list[dict[str, str]]):
    for idx, court in enumerate(courts_config):
        logger.info("Processing " + court.get("alias") + " with parser " + court.get("parser_type") + ", " + str(
            idx + 1) + "/" + str(len(courts_config)))
        if court.get("parser_type") == "1":
            parser_type_1(court)
        elif court.get("parser_type") == "2":
            parser_type_2(court)
        elif court.get("parser_type") == "3":
            parser_type_3(court)
        elif court.get("parser_type") == "4":
            parser_type_4(court)


def main() -> None:
    courts_config = read_courts_config()
    scrap_courts(courts_config)


if __name__ == "__main__":
    main()
