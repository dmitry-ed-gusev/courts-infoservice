import os
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text as sa_text
from pandas import DataFrame

from court_cases_scraper.src.courts.config import scraper_config, db_init_config


def clean_stage_table(db_config: dict[str, str]):
    """cleans stage table"""
    logger.debug("Cleaning stage table.")
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")

    connection = engine.connect()
    sql = "delete from " + scraper_config.STAGE_TABLE
    connection.execute(sa_text(sql))
    connection.commit()
    connection.close()
    logger.debug("Stage table cleaned.")


def log_scrapped_court(db_config: dict[str, str], court_alias: str, check_date: datetime, status: str) -> None:
    """adds court scrap to log"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")

    connection = engine.connect()
    sql = sa_text("insert into config_court_cases_scrap_log (court, check_date, status, load_dttm)"
                  "values (:court_alias, :check_date, :status, now())")
    connection.execute(sql, {"court_alias": court_alias, "check_date": check_date, "status": status})
    connection.commit()
    connection.close()


def calculate_row_hash_stage(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    connection = engine.connect()
    sql = "call stage_p_update_court_cases_row_hash()"
    connection.execute(sa_text(sql))
    connection.commit()
    connection.close()


def load_to_dm(db_config: dict[str, str], court_alias: str, check_date: datetime) -> None:
    """calls load to dm procedure"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")

    logger.debug("Connected. Starting merge to DM")
    connection = engine.connect()
    sql = sa_text("call dm_p_load_court_cases(:court_alias, :check_date)")
    params = {"court_alias": court_alias, "check_date": check_date.strftime("%d.%m.%Y")}
    connection.execute(sql, params)
    connection.commit()
    connection.close()
    logger.debug("Merge to DM completed.")


def read_courts_config(db_config: dict[str, str]) -> list[dict[str, str]]:
    """reads court config from db"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    connection = engine.connect()

    logger.debug("Connected. Reading courts config from DB.")
    result = []
    sql = sa_text("select link, title, alias, server_num, parser_type, check_date "
                  "from config_v_courts_to_refresh "
                  "where check_date between :start_date and :end_date "
                  "order by check_date")
    params = {"start_date": datetime.now() - timedelta(days=scraper_config.RANGE_BACKWARD),
              "end_date": datetime.now() + timedelta(days=scraper_config.RANGE_FORWARD)}
    result_1 = connection.execute(sql, params)
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
    connection.close()
    return result


def load_to_stage(data_frame: DataFrame, db_config: dict[str, str]) -> None:
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
    connection = engine.connect()
    logger.debug("Loading to stage")
    data_frame.to_sql(scraper_config.STAGE_TABLE, engine, index=False, if_exists="append")

    # trying to find case_num in our dm
    connection.execute(sa_text("call stage_p_update_case_num()"))
    connection.commit()
    # calculate row hash
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
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    connection = engine.connect()
    logger.debug("Connected")
    os.chdir(Path(db_init_config.SQL_SCRIPTS_DIR))
    is_empty = False
    if not force:
        try:
            connection.execute(db_init_config.TEST_DB_QUERY)
        except:
            is_empty = True
    if force or is_empty:
        for file in db_init_config.INIT_FILES:
            with open(file, 'r', encoding="utf-8") as sql_file:
                sql = sa_text(" ".join(sql_file.readlines()))
                logger.debug(sql)
                connection.execute(sql)

        connection.commit()
    connection.close()
