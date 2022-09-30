"""
parse court data and load to stage
"""
import argparse
import pymysql
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from loguru import logger

from court_cases_scrapper import config

logger.debug("Connecting to db")

conn = pymysql.connect(host=config.MYSQL_CONNECT["host"],
                       port=config.MYSQL_CONNECT["port"],
                       user=config.MYSQL_CONNECT["user"],
                       passwd=config.MYSQL_CONNECT["passwd"]
                       )

logger.debug("Connected")
cursor = conn.cursor()


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
            select cfg.link, cfg.title, cfg.alias
            from dm.court_scrap_config cfg
                left join max_load_date log
            	    on cfg.alias = log.court
            where not skip
            	and (log.court is null or date_add(now(), interval -1 day) > log.load_dttm)
            """)
    result_1 = cursor.fetchall()
    if result_1:
        for row1 in result_1:
            result.append({"link": row1[0], "title": row1[1], "alias": row1[2]})

    return result


def clean_stage_table():
    """clean stage table"""
    logger.debug("Cleaning stage table " + config.STAGE_TABLE)
    sql = "delete from " + config.STAGE_TABLE
    cursor.execute(sql)
    logger.debug("Stage table cleaned")
    conn.commit()


def load_to_stage(data: list[dict[str, str]]) -> None:
    """loads parsed data to stage"""
    sql_part1 = f"INSERT INTO {config.STAGE_TABLE} ("
    sql_part2 = ""

    for field in config.STAGE_MAPPING:
        sql_part1 = sql_part1 + field.get("name") + ", "
        if field.get("constant"):
            sql_part2 = sql_part2 + field.get("constant") + ", "
        else:
            sql_part2 = sql_part2 + "%s, "

    sql_statement = sql_part1.rstrip(", ") + ") VALUES (" + sql_part2.rstrip(", ") + ")"

    logger.debug(sql_statement)

    logger.info("Data load start")
    for idx_r, row in enumerate(data):
        values = []
        for idx_c, col in enumerate(config.STAGE_MAPPING):
            if row.get(col.get("mapping")):
                values.append(row.get(col.get("mapping")))
            elif col.get("mapping"):
                values.append(None)
        cursor.execute(sql_statement, values)
        if idx_r % config.COMMIT_INTERVAL == 0 and idx_r > 0:
            conn.commit()
            logger.debug("Commit " + str(idx_r))
    conn.commit()

    logger.info("Data load completed")


def daterange(date1: str, date2: str) -> list[datetime]:
    d_date1 = datetime.strptime(date1, '%Y-%m-%d')
    d_date2 = datetime.strptime(date2, '%Y-%m-%d')
    result = []
    for n in range(int((d_date2 - d_date1).days) + 1):
        result.append((d_date1 + timedelta(days=n)))

    return result


def parse_page(page: requests.Response, court: dict, check_date: str) -> list[dict[str, str]]:
    """parses output page"""
    result = []
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("div", id="tablcont")
    logger.info("Processing " + court.get("alias") + ", date " + check_date)
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
                        result_row["col" + str(idx_r)] = row.text
                    else:
                        result_row["col" + str(idx_r)] = str(row.contents)
                    if row.find(href=True):
                        result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result.append(result_row)
    return result


def scrap_courts(date_from: str, date_to: str, court_filter: str, courts_config: list[dict[str, str]]):
    session = requests.Session()
    session.headers = {"user-agent": config.USER_AGENT}
    for court in courts_config:
        if court_filter and court.get("alias") != court_filter:
            continue
        result = []
        for date in daterange(date_from, date_to):

            check_date = date.strftime("%d.%m.%Y")
            page = session.get(court.get("link") + "&H_date=" + check_date)
            result = result + parse_page(page, court, check_date)
            if len(result) > 50000:
                load_to_stage(result)
                result = []
        load_to_stage(result)
        sql = "insert into dm.court_cases_scrap_log (court, load_dttm) values ('" + court.get("alias") + "', now())"
        cursor.execute(sql)
        conn.commit()


def parse_args() -> argparse.Namespace:
    """Parser for command-line options, arguments and sub-commands."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--court", type=str, required=False)
    parser.add_argument("--date_from", type=str, required=False,
                        default=(datetime.now() - timedelta(days=config.RANGE_BACKWARD)).strftime("%Y-%m-%d"))
    parser.add_argument("--date_to", type=str, required=False,
                        default=(datetime.now() + timedelta(days=config.RANGE_FORWARD)).strftime("%Y-%m-%d"))
    parsed_args = parser.parse_args()

    return parsed_args


def main() -> None:
    args = parse_args()
    courts_config = read_courts_config()
    clean_stage_table()
    scrap_courts(args.date_from, args.date_to, args.court, courts_config)
    load_to_dm()


if __name__ == "__main__":
    main()
