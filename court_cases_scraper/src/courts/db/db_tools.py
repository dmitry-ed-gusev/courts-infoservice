import os
from pathlib import Path
import pymysql
from loguru import logger
from datetime import datetime, timedelta

from court_cases_scraper.src.courts.config import scraper_config as config
from court_cases_scraper.src.courts.config import db_init_config


def log_scrapped_court(db_config: dict[str, str], court_alias: str, check_date: datetime) -> None:
    """adds court scrap to log"""
    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    cursor = conn.cursor()
    sql = ("insert into config_court_cases_scrap_log (court, check_date, load_dttm)"
           "values (%(court_alias)s, %(check_date)s, now())")
    cursor.execute(sql, {"court_alias": court_alias, "check_date": check_date})
    conn.commit()
    conn.close()


def calculate_row_hash_stage(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""

    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
    sproc = "stage_p_update_court_cases_row_hash"
    cursor.execute(sproc)
    conn.commit()
    conn.close()


def load_to_dm(db_config: dict[str, str], court_alias: str, check_date: datetime) -> None:
    """calls load to dm procedure"""
    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    logger.debug("Connected. Starting merge to DM")
    cursor = conn.cursor()
    sql = "call dm_p_load_court_cases(%(court_alias)s, %(check_date)s)"
    cursor.execute(sql, {"court_alias": court_alias, "check_date": check_date.strftime("%d.%m.%Y")})
    conn.commit()
    conn.close()
    logger.debug("Merge to DM completed.")


def read_courts_config(db_config: dict[str, str]) -> list[dict[str, str]]:
    """reads court config from db"""
    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    logger.debug("Connected. Reading courts config from DB.")
    cursor = conn.cursor()
    result = []
    cursor.execute("""
            select link, title, alias, server_num, parser_type, check_date
            from config_v_courts_to_refresh
            where check_date between %(start_date)s and %(end_date)s
            order by check_date
            """, {"start_date": datetime.now() - timedelta(days=config.RANGE_BACKWARD),
                  "end_date": datetime.now() + timedelta(days=config.RANGE_FORWARD)})
    result_1 = cursor.fetchall()
    if result_1:
        for row1 in result_1:
            result.append(
                {"link": row1[0],
                 "title": row1[1],
                 "alias": row1[2],
                 "server_num": row1[3],
                 "parser_type": row1[4],
                 "check_date": row1[5]}
            )
    logger.debug("Config read completed.")
    conn.close()
    return result


def load_to_stage(data: list[dict[str, str]], stage_mapping: list[dict[str, str]], db_config: dict[str, str],
                  court_alias: str, check_date: datetime) -> None:
    """loads parsed data to stage"""
    if len(data) == 0:
        return

    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
    sql = f"delete from {config.STAGE_TABLE} where court_alias=%(court_alias)s and check_date=%(check_date)s"
    cursor.execute(sql, {"court_alias": court_alias, "check_date": check_date.strftime("%d.%m.%Y")})
    conn.commit()

    sql_part1 = f"INSERT INTO {config.STAGE_TABLE} ("
    sql_part2 = ""

    for field in stage_mapping:
        sql_part1 = sql_part1 + field.get("name") + ", "
        if field.get("constant"):
            sql_part2 = sql_part2 + field.get("constant") + ", "
        else:
            sql_part2 = sql_part2 + "%s, "

    sql_statement = sql_part1.rstrip(", ") + ") VALUES (" + sql_part2.rstrip(", ") + ")"

    # logger.debug(sql_statement)

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
    cursor.callproc("stage_p_update_court_cases_row_hash")
    conn.commit()
    logger.debug("Stage data load completed. Loaded " + str(len(data)) + " rows.")
    conn.close()


def init_db(db_config: dict[str, str], force: bool = False) -> None:
    """executes sql scripts to init db structure"""
    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
    os.chdir(Path(db_init_config.SQL_SCRIPTS_DIR))
    is_empty = False
    if not force:
        try:
            cursor.execute(db_init_config.TEST_DB_QUERY)
        except pymysql.Error:
            is_empty = True
    if force or is_empty:
        for file in db_init_config.INIT_FILES:
            with open(file, 'r', encoding="utf-8") as sql_file:
                sql = " ".join(sql_file.readlines())
                logger.debug(sql)
                cursor.execute(sql)

        conn.commit()
    conn.close()
