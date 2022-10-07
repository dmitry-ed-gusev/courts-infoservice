import os
import pymysql
from loguru import logger

from court_cases_scraper.src.courts.config import scraper_config as config


def calculate_row_hash_stage(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    logger.debug("Connecting to db")

    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd")
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
    sql = "call stage.p_update_court_cases_row_hash()"
    cursor.execute(sql)
    conn.commit()


def load_to_dm(db_config: dict[str, str]) -> None:
    """calls load to dm procedure"""
    logger.debug("Connecting to db")

    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd")
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
    sql = "call dm.p_load_court_cases()"
    cursor.execute(sql)
    conn.commit()


def read_courts_config(db_config: dict[str, str]) -> list[dict[str, str]]:
    """reads court config from db"""
    logger.debug("Connecting to db")

    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd")
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
    result = []
    cursor.execute("""
            select link, title, alias, server_num, parser_type
            from dm.v_courts_to_refresh
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


def clean_stage_table(db_config: dict[str, str]) -> None:
    """clean stage table"""
    logger.debug("Connecting to db")

    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd")
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
    logger.debug("Cleaning stage table " + config.STAGE_TABLE)
    sql = "delete from " + config.STAGE_TABLE
    cursor.execute(sql)
    logger.debug("Stage table cleaned")
    conn.commit()


def load_to_stage(data: list[dict[str, str]], stage_mapping: list[dict[str, str]], db_config: dict[str, str]) -> None:
    """loads parsed data to stage"""
    logger.debug("Connecting to db")

    conn = pymysql.connect(host=db_config.get("host"),
                           port=int(db_config.get("port")),
                           user=db_config.get("user"),
                           passwd=db_config.get("passwd")
                           )

    logger.debug("Connected")
    cursor = conn.cursor()
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
