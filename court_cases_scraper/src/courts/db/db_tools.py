import os
from pathlib import Path
import pymysql
from loguru import logger
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text as sa_text
from pandas import DataFrame

from court_cases_scraper.src.courts.config import scraper_config, db_init_config


def clean_stage_table(db_config: dict[str, str]):
    """cleans stage table"""
    logger.debug("Cleaning stage table.")
    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    cursor = conn.cursor()
    sql = "delete from " + scraper_config.STAGE_TABLE
    cursor.execute(sql)
    conn.commit()
    conn.close()
    logger.debug("Stage table cleaned.")


def log_scrapped_court(db_config: dict[str, str], court_alias: str, check_date: datetime, status: str) -> None:
    """adds court scrap to log"""
    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd"),
                           database=db_config.get("db"),
                           )

    cursor = conn.cursor()
    sql = ("insert into config_court_cases_scrap_log (court, check_date, status, load_dttm)"
           "values (%(court_alias)s, %(check_date)s, %(status)s, now())")
    cursor.execute(sql, {"court_alias": court_alias, "check_date": check_date, "status": status})
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
            """, {"start_date": datetime.now() - timedelta(days=scraper_config.RANGE_BACKWARD),
                  "end_date": datetime.now() + timedelta(days=scraper_config.RANGE_FORWARD)})
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


def load_to_stage_alchemy(data_frame: DataFrame, db_config: dict[str, str]) -> None:
    """loads parsed data to stage"""
    if len(data_frame) == 0:
        return
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    logger.debug("Loading to stage")
    data_frame.to_sql(scraper_config.STAGE_TABLE, engine, index=False, if_exists="append")

    connection = engine.connect()
    connection.execute(sa_text("call stage_p_update_court_cases_row_hash()"))
    connection.commit()
    logger.debug("Loaded " + str(len(data_frame)) + " rows to stage.")
    connection.close()


def convert_data_to_df(data: list[dict[str, str]], stage_mapping: list[dict[str, str]]) -> DataFrame:
    values = []
    for idx_r, row in enumerate(data):
        value = {}
        for idx_c, col in enumerate(stage_mapping):
            if row.get(col.get("mapping")):
                value[col["name"]] = row.get(col.get("mapping"))
            elif col.get("mapping"):
                value[col["name"]] = None
        values.append(value)
    data_frame = DataFrame(values)
    return data_frame


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
