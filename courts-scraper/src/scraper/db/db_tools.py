import math
import os
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger
from pandas import DataFrame, read_sql_query, read_sql_table
from sqlalchemy import Engine, create_engine
from sqlalchemy import text as sa_text

from scraper.config import db_init_config, scraper_config


def get_db_engine(db_config: dict[str, str]) -> Engine:
    """returns sqlalchemy db_engine"""
    if db_config["engine_type"] == "mysql":
        # dialect - mysql, sql driver - pymysql
        return create_engine(
            "mysql+pymysql://"
            + db_config["user"]
            + ":"
            + db_config["passwd"]
            + "@"
            + db_config["host"]
            + ":"
            + db_config["port"]
            + "/"
            + db_config["db"]
            + "?charset=utf8&local_infile=1"
        )
    if db_config["engine_type"] in ("ora", "oracle"):
        # dialect - oracle, sql driver - cx_oracle
        return create_engine(
            "oracle+cx_oracle://"
            + db_config["user"]
            + ":"
            + db_config["passwd"]
            + "@"
            + db_config["host"]
            + ":"
            + db_config["port"]
            + "/?service_name="
            + db_config["db"]
        )
    raise Exception("Engine " + db_config["engine_type"] + " not supported")


def clean_stage_courts_table(db_config: dict[str, str]):
    """cleans stage courts table"""
    logger.debug("Cleaning stage courts table.")
    engine = get_db_engine(db_config)

    connection = engine.connect()
    sql = "truncate table " + scraper_config.STAGE_TABLE
    connection.execute(sa_text(sql))
    connection.commit()
    connection.close()
    logger.debug("Stage courts table cleaned.")


def clean_stage_links_table(db_config: dict[str, str]):
    """cleans stage links table"""
    logger.debug("Cleaning stage links table.")
    engine = get_db_engine(db_config)

    connection = engine.connect()
    sql = "truncate table " + scraper_config.LINKS_STAGE_TABLE
    connection.execute(sa_text(sql))
    connection.commit()
    connection.close()
    logger.debug("Stage links table cleaned.")


def log_scrapped_court(
    db_config: dict[str, str], court_alias: str, check_date: datetime, status: str
) -> None:
    """adds court scrap to log"""
    engine = get_db_engine(db_config)

    connection = engine.connect()
    sql = sa_text(
        "insert into config_court_cases_scrap_log (court, check_date, status, load_dttm)"
        "values (:court_alias, :check_date, :status, now())"
    )
    connection.execute(
        sql, {"court_alias": court_alias, "check_date": check_date, "status": status}
    )
    connection.commit()
    connection.close()


def etl_load_court_cases_dq(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = get_db_engine(db_config)
    connection = engine.connect()
    # lnd -> stg
    logger.info("Loading court cases data from lnd to stg.")
    sql = sa_text("call stage_p_load_stg_court_cases()")
    connection.execute(sql)
    connection.commit()
    # trying to find case_num in our dm
    logger.info("Performing DQ tasks")
    sql = sa_text("call stage_p_update_case_num()")
    connection.execute(sql)
    connection.commit()
    connection.close()


def etl_load_court_cases_dv(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = get_db_engine(db_config)
    connection = engine.connect()
    # stg -> dv
    logger.info("Loading court cases data from stg to dv.")
    sql = sa_text("call dv_p_load_court_cases_h()")
    logger.info("Calling " + sql.text)
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dv_p_load_court_cases_l()")
    logger.info("Calling " + sql.text)
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dv_p_load_court_cases_ls()")
    logger.info("Calling " + sql.text)
    connection.execute(sql)
    connection.commit()
    connection.close()
    logger.info("Court cases data loaded to dv.")


def etl_load_court_cases_dm(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = get_db_engine(db_config)
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


def etl_load_case_links_dq(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = get_db_engine(db_config)
    connection = engine.connect()
    # lnd -> stg
    logger.info("Loading case links data from lnd to stg.")
    sql = sa_text("call stage_p_load_stg_case_links()")
    connection.execute(sql)
    connection.commit()
    # trying to find case_num in our dm
    # logger.info("Performing DQ tasks")
    connection.close()


def etl_load_case_links_dv(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = get_db_engine(db_config)
    connection = engine.connect()
    # stg -> dv
    logger.info("Loading case links data from stg to dv.")
    sql = sa_text("call dv_p_load_case_link_h()")
    logger.info(f"Calling {sql}")
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dv_p_load_case_link_hs()")
    logger.info(f"Calling {sql}")
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dv_p_load_case_link_l()")
    logger.info(f"Calling {sql}")
    connection.execute(sql)
    connection.commit()
    sql = sa_text("call dv_p_load_case_link_ls()")
    logger.info(f"Calling {sql}")
    connection.execute(sql)
    connection.commit()

    connection.close()
    logger.info("Case links data loaded to dv.")


def etl_load_case_links_dm(db_config: dict[str, str]) -> None:
    """calcs row hash in stage"""
    engine = get_db_engine(db_config)
    connection = engine.connect()
    # stg -> dv
    logger.info("Loading case links data from dv to dm.")
    sql = sa_text("call dm_p_load_case_links()")
    connection.execute(sql)
    connection.commit()
    connection.close()
    logger.info("Case links data loaded to dm.")


def read_courts_config(db_config: dict[str, str]) -> list[dict[str, str]]:
    """reads court config from db"""
    engine = get_db_engine(db_config)
    connection = engine.connect()

    logger.debug("Connected. Reading courts config from DB.")
    result = []
    sql = sa_text(
        "select link, title, alias, server_num, parser_type, check_date "
        "from config_v_courts_to_refresh "
        "where check_date between :start_date and :end_date "
        "order by check_date"
    )
    params = {
        "start_date": datetime.now() - timedelta(days=scraper_config.RANGE_BACKWARD),
        "end_date": datetime.now() + timedelta(days=scraper_config.RANGE_FORWARD),
    }
    result_1 = connection.execute(sql, params)
    if result_1:
        for row1 in result_1:
            result.append(
                {
                    "link": row1[0],
                    "title": row1[1],
                    "alias": row1[2],
                    "server_num": row1[3],
                    "parser_type": row1[4],
                    "check_date": row1[5],
                }
            )
    logger.debug("Courts config read completed.")
    connection.close()
    return result


def read_links_config(db_config: dict[str, str]) -> list[dict[str, str]]:
    """reads court config from db"""
    engine = get_db_engine(db_config)
    connection = engine.connect()

    logger.debug("Connected. Reading links config from DB.")
    result = []
    sql = sa_text(
        "select case_link, case_num, parser_type, link, court_alias "
        "from config_v_links_to_refresh "
        # "limit 100000"
    )
    result_1 = connection.execute(sql)
    if result_1:
        for row1 in result_1:
            result.append(
                {
                    "case_link": row1[0],
                    "case_num": row1[1],
                    "parser_type": row1[2],
                    "link": row1[3],
                    "alias": row1[4],
                }
            )
    logger.debug("Links config read completed.")
    connection.close()
    return result


def load_courts_to_stage(
    data_frame: DataFrame,
    db_config: dict[str, str],
    court_alias: str,
    check_date: datetime,
) -> None:
    """loads parsed data to stage"""
    if len(data_frame) == 0:
        return
    engine = get_db_engine(db_config)
    connection = engine.connect()
    logger.debug("Loading courts to stage")
    # delete same data chunk from stage
    sql = sa_text(
        f"delete from {scraper_config.STAGE_TABLE} where court_alias = :court_alias and check_date = :check_date"
    )
    params = {"court_alias": court_alias, "check_date": check_date.strftime("%d.%m.%Y")}
    connection.execute(sql, params)
    connection.commit()
    # load dataframe to stage table
    data_frame.to_sql(
        name=scraper_config.STAGE_TABLE, con=connection, index=False, if_exists="append"
    )
    connection.commit()
    logger.debug("Loaded " + str(len(data_frame)) + " rows to stage.")
    connection.close()


def load_links_to_stage(data_frame: DataFrame, db_config: dict[str, str]) -> None:
    """loads parsed data to stage"""
    if len(data_frame) == 0:
        return
    engine = get_db_engine(db_config)
    connection = engine.connect()
    logger.debug("Loading links to stage")
    data_frame.to_sql(
        scraper_config.LINKS_STAGE_TABLE, engine, index=False, if_exists="append"
    )
    logger.debug("Loaded " + str(len(data_frame)) + " rows to stage.")
    connection.close()


def deactivate_outdated_bot_log_entries(db_config: dict[str, str]) -> None:
    """calls log deactivation procedure"""
    engine = get_db_engine(db_config)

    logger.debug("Connected. Deactivating tg bot log entries.")
    connection = engine.connect()
    sql = sa_text("call config_p_deactivate_outdated_tg_bot_log_entries()")
    connection.execute(sql)
    connection.commit()
    connection.close()
    logger.debug("Deactivation tg bot log entries completed.")


def transfer_dm_from_wrk_to_host(
    db_config_wrk: dict[str, str],
    db_config: dict[str, str],
    tables_list: list[dict[str, str]],
) -> None:
    """transfer data marts from work db to hosting dn"""
    engine_wrk = get_db_engine(db_config_wrk)
    engine = get_db_engine(db_config)
    connection = engine.connect()
    connection_wrk = engine_wrk.connect()
    for table_dict in tables_list:
        table = table_dict["table_name"]
        sql = sa_text(f"truncate table {table}_old")
        connection.execute(sql)
        connection.commit()

        logger.info(f"Transferring data: {table}")
        if table_dict.get("split_key"):
            key_name = table_dict["split_key"]
            sql = sa_text(
                f"select min({key_name}) as min_val, max({key_name}) as max_val from {table}_old"
            )
            result = connection_wrk.execute(sql)
            min_val = max_val = 0
            for row in result:
                min_val: int = row[0]
                max_val: int = row[1]
                break

            parts: int = math.ceil((max_val - min_val) / scraper_config.BULK_SIZE_ROWS)
            for part in range(0, parts):
                low_bound = min_val + part * scraper_config.BULK_SIZE_ROWS
                up_bound = min_val + (1 + part) * scraper_config.BULK_SIZE_ROWS
                logger.info(
                    f"Reading chunk {str(part+1)} of {str(parts+1)}: {key_name} keys between {low_bound} and {up_bound}..."
                )
                sql = sa_text(
                    f"select * from {table} where {key_name} >= {low_bound} and {key_name} < {up_bound}"
                )
                source_data = read_sql_query(sql, connection_wrk)
                logger.info(f"Read {str(len(source_data))} rows")
                source_data.to_sql(
                    table + "_old", connection, index=False, if_exists="append"
                )
                connection.commit()
        else:
            source_data = read_sql_table(table, connection_wrk)
            logger.info(f"Read {str(len(source_data))} rows")
            source_data.to_sql(
                table + "_old", connection, index=False, if_exists="append"
            )
            connection.commit()

        logger.info("Data loaded to target db.")

    connection.close()
    connection_wrk.close()


def switch_dm_tables(
    db_config_wrk: dict[str, str],
    db_config: dict[str, str],
    tables_list: list[dict[str, str]],
) -> None:
    engine_wrk = get_db_engine(db_config_wrk)
    engine = get_db_engine(db_config)
    connection = engine.connect()
    connection_wrk = engine_wrk.connect()
    logger.info("Renaming tables...")
    for table_dict in tables_list:
        table = table_dict["table_name"]
        sql = sa_text(f"rename table {table}_old to {table}_new")
        connection.execute(sql)
        sql = sa_text(f"rename table {table} to {table}_old")
        connection.execute(sql)
        sql = sa_text(f"rename table {table}_new to {table}")
        connection.execute(sql)
        logger.info("Tables renamed.")
        sql = sa_text(f"truncate table {table}_old")
        connection.execute(sql)
        connection.commit()

    connection.close()
    connection_wrk.close()


def convert_data_to_df(
    data: list[dict[str, str]], stage_mapping: list[dict[str, str]]
) -> DataFrame:
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
    engine = get_db_engine(db_config)
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
            with open(file, "r", encoding="utf-8") as sql_file:
                sql = sa_text(" ".join(sql_file.readlines()))
                logger.debug(sql)
                connection.execute(sql)

        connection.commit()
    connection.close()
