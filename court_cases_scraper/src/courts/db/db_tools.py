import os
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text as sa_text
from pandas import DataFrame

from court_cases_scraper.src.courts.config import scraper_config, db_init_config


def clean_stage_courts_table(db_config: dict[str, str]):
    """cleans stage courts table"""
    logger.debug("Cleaning stage courts table.")
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
    logger.debug("Stage courts table cleaned.")


def clean_stage_links_table(db_config: dict[str, str]):
    """cleans stage links table"""
    logger.debug("Cleaning stage links table.")
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")

    connection = engine.connect()
    sql = "delete from " + scraper_config.LINKS_STAGE_TABLE
    connection.execute(sa_text(sql))
    connection.commit()
    connection.close()
    logger.debug("Stage links table cleaned.")


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


def etl_load_court_cases_dq(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    connection = engine.connect()
    # lnd -> stg
    logger.info("Loading court cases data from lnd to stg.")
    sql = sa_text("call stage_p_load_stg_court_cases()")
    connection.execute(sql)
    connection.commit()
    # trying to find case_num in our dm
    logger.info("Performing DQ tasks")
    connection.execute(sa_text("call stage_p_update_case_num()"))
    connection.commit()
    connection.close()


def etl_load_court_cases_dv(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    connection = engine.connect()
    # stg -> dv
    logger.info("Loading court cases data from stg to dv.")
    sql = sa_text("call dv_p_load_court_cases_h()")
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dv_p_load_court_cases_l()")
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dv_p_load_court_cases_ls()")
    connection.execute(sql)
    connection.commit()
    connection.close()
    logger.info("Court cases data loaded to dv.")


def etl_load_court_cases_dm(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    connection = engine.connect()
    # stg -> dv
    logger.info("Loading court cases data from dv to dm.")
    sql = sa_text("call dm_p_load_court_cases()")
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dm_p_fill_court_case_stats()")
    connection.execute(sql)
    connection.commit()
    connection.close()
    logger.info("Court cases data loaded to dm.")


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
    logger.debug("Courts config read completed.")
    connection.close()
    return result


def read_links_config(db_config: dict[str, str]) -> list[dict[str, str]]:
    """reads court config from db"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")
    connection = engine.connect()

    logger.debug("Connected. Reading links config from DB.")
    result = []
    sql = sa_text("select case_link, case_num, parser_type, link "
                  "from config_v_links_to_refresh "
                  )
    result_1 = connection.execute(sql)
    if result_1:
        for row1 in result_1:
            result.append(
                {"case_link": row1[0],
                 "case_num": row1[1],
                 "parser_type": row1[2],
                 "link": row1[3],
                 }
            )
    logger.debug("Links config read completed.")
    connection.close()
    return result


def load_courts_to_stage(data_frame: DataFrame,
                         db_config: dict[str, str],
                         court_alias: str,
                         check_date: datetime) -> None:
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
    logger.debug("Loading courts to stage")
    # delete same data chunk from stage
    sql = sa_text(
        f"delete from {scraper_config.STAGE_TABLE} where court_alias = :court_alias and check_date = :check_date")
    params = {"court_alias": court_alias, "check_date": check_date.strftime("%d.%m.%Y")}
    connection.execute(sql, params)
    connection.commit()
    # load dataframe to stage table
    data_frame.to_sql(scraper_config.STAGE_TABLE, engine, index=False, if_exists="append")
    logger.debug("Loaded " + str(len(data_frame)) + " rows to stage.")
    connection.close()


def load_courts_to_dm(db_config: dict[str, str], court_alias: str, check_date: datetime) -> None:
    """calls load to dm procedure"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")

    logger.debug("Connected. Starting merge courts to DM")
    connection = engine.connect()
    sql = sa_text("call dm_p_load_court_cases(:court_alias, :check_date)")
    params = {"court_alias": court_alias, "check_date": check_date.strftime("%d.%m.%Y")}
    connection.execute(sql, params)
    connection.commit()
    connection.close()
    logger.debug("Merge to DM completed.")


def load_links_to_stage(data_frame: DataFrame, db_config: dict[str, str]) -> None:
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
    logger.debug("Loading links to stage")
    data_frame.to_sql(scraper_config.LINKS_STAGE_TABLE, engine, index=False, if_exists="append")
    logger.debug("Loaded " + str(len(data_frame)) + " rows to stage.")
    connection.close()


def load_links_to_dm(db_config: dict[str, str]) -> None:
    """calls load to dm procedure"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")

    logger.debug("Connected. Starting merge links to DM")
    connection = engine.connect()
    sql = sa_text("call dm_p_load_case_links()")
    connection.execute(sql)
    connection.commit()
    connection.close()
    logger.debug("Merge to DM completed.")


def deactivate_outdated_bot_log_entries(db_config: dict[str, str], court_alias: str, check_date: datetime) -> None:
    """calls log deactivation procedure"""
    engine = create_engine("mysql+pymysql://"
                           + db_config.get("user")
                           + ":" + db_config.get("passwd")
                           + "@" + db_config.get("host")
                           + ":" + db_config.get("port")
                           + "/" + db_config.get("db")
                           + "?charset=utf8&local_infile=1")

    logger.debug("Connected. Deactivating tg bot log entries.")
    connection = engine.connect()
    sql = sa_text("call config_p_deactivate_outdated_tg_bot_log_entries(:court_alias, :check_date)")
    params = {"court_alias": court_alias, "check_date": check_date}
    connection.execute(sql, params)
    connection.commit()
    connection.close()
    logger.debug("Deactivation tg bot log entries completed.")


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
