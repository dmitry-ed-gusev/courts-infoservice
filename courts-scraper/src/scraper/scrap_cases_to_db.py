"""
parse court data and load to stage
"""
import os
import sys
import threading
import time
import argparse
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger

from scraper.config import scraper_config
from scraper.db import db_tools
from scraper.parsers import (
    parser_1,
    parser_2,
    parser_3,
    parser_4,
    parser_5,
    parser_6,
    parser_7,
    parser_8,
    parser_9,
)
from scraper.utils.utilities import threadsafe_function

logger.remove()
# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def thread_count(futures: list[Future]) -> tuple[int, int, int]:
    """count running threads"""
    running = 0
    done = 0
    for future in futures:
        if future.running():
            running += 1
        if future.done():
            done += 1
    total = len(futures)
    return running, done, total


def scrap_courts_no_parallel(
    courts_config: list[dict[str, str | datetime]], db_config: dict[str, str]
):
    """router with parallel execution"""

    for idx, court in enumerate(courts_config):
        logger.info(
            "Processing "
            + court["alias"]
            + " date "
            + court["check_date"].strftime("%d.%m.%Y")
            + " with parser "
            + court["parser_type"]
            + ", "
            + str(idx + 1)
            + "/"
            + str(len(courts_config))
        )
        if court["parser_type"] == "1":
            result_part, court_config, status = parser_1.parse_page(court)
        elif court["parser_type"] == "2":
            result_part, court_config, status = parser_2.parse_page(court)
        elif court["parser_type"] == "3":
            result_part, court_config, status = parser_3.parse_page(court)
        elif court["parser_type"] == "4":
            result_part, court_config, status = parser_4.parse_page(court)
        elif court["parser_type"] == "5":
            result_part, court_config, status = parser_5.parse_page(court)
        elif court["parser_type"] == "6":
            result_part, court_config, status = parser_6.parse_page(court)
        elif court["parser_type"] == "7":
            result_part, court_config, status = parser_7.parse_page(court)
        elif court["parser_type"] == "8":
            result_part, court_config, status = parser_8.parse_page(court)
        elif court["parser_type"] == "9":
            result_part, court_config, status = parser_9.parse_page(court)
        else:
            continue
        result_len = len(result_part)
        if result_len > 0:
            db_tools.load_courts_to_stage(
                result_part,
                db_config,
                court_config["alias"],
                court_config["check_date"],
            )
        if status == "success":
            logger.info(
                "Parser "
                + court_config["parser_type"]
                + " court "
                + court_config["alias"]
                + " date "
                + court_config["check_date"].strftime("%d.%m.%Y")
                + " loaded. Total records "
                + str(result_len)
            )
        elif status == "failure":
            logger.warning(
                "Parser "
                + court_config["parser_type"]
                + " court "
                + court_config["alias"]
                + " date "
                + court_config["check_date"].strftime("%d.%m.%Y")
                + " failed."
            )
        db_tools.log_scrapped_court(
            db_config, court_config["alias"], court_config["check_date"], status
        )


@threadsafe_function
def scrap_courts(
    courts_config: list[dict[str, str | datetime]], db_config: dict[str, str]
):
    """router with parallel execution"""
    futures = []  # list to store future results of threads
    executor1 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[1]["workers_count"]
    )
    executor2 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[2]["workers_count"]
    )
    executor3 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[3]["workers_count"]
    )
    executor4 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[4]["workers_count"]
    )
    executor5 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[5]["workers_count"]
    )
    executor6 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[6]["workers_count"]
    )
    executor7 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[7]["workers_count"]
    )
    executor8 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[8]["workers_count"]
    )
    executor9 = ThreadPoolExecutor(
        max_workers=scraper_config.SCRAPER_CONFIG[9]["workers_count"]
    )
    for court in courts_config:
        if court["parser_type"] == "1":
            future = executor1.submit(parser_1.parse_page, court)
        elif court["parser_type"] == "2":
            future = executor2.submit(parser_2.parse_page, court)
        elif court["parser_type"] == "3":
            future = executor3.submit(parser_3.parse_page, court)
        elif court["parser_type"] == "4":
            future = executor4.submit(parser_4.parse_page, court)
        elif court["parser_type"] == "5":
            future = executor5.submit(parser_5.parse_page, court)
        elif court["parser_type"] == "6":
            future = executor6.submit(parser_6.parse_page, court)
        elif court["parser_type"] == "7":
            future = executor7.submit(parser_7.parse_page, court)
        elif court["parser_type"] == "8":
            future = executor8.submit(parser_8.parse_page, court)
        elif court["parser_type"] == "9":
            future = executor9.submit(parser_9.parse_page, court)
        else:
            continue
        futures.append(future)
    loaded = failed = 0
    for task in as_completed(futures):
        running, done, total = thread_count(futures)
        logger.info(
            f"{running} running. {done} completed. {loaded} loaded. {failed} failed. Total {total}. "
            + str(round(done / total * 100, 2))
            + "% scrapped. "
            + str(round(loaded / (total - failed) * 100, 2))
            + "% loaded."
        )
        try:
            result_part, court_config, status = task.result()
        except Exception as ue:
            logger.warning(
                "Unexpected error in one of the workers. Skipping. Error:\n" + str(ue)
            )
            failed += 1
            continue
        result_len = len(result_part)
        if result_len > 0:
            while True:
                try:
                    db_tools.load_courts_to_stage(
                        result_part,
                        db_config,
                        court_config["alias"],
                        court_config["check_date"],
                    )
                    break
                except Exception as e_stg:
                    logger.warning(
                        "Failed to load data to stage. Retry in 3 seconds - "
                        + str(e_stg)
                    )
                    time.sleep(3)
        if status == "success":
            logger.info(
                "Parser "
                + court_config["parser_type"]
                + " court "
                + court_config["alias"]
                + " date "
                + court_config["check_date"].strftime("%d.%m.%Y")
                + " loaded. Total records "
                + str(result_len)
            )
            loaded += 1
        elif status == "failure":
            logger.warning(
                "Parser "
                + court_config["parser_type"]
                + " court "
                + court_config["alias"]
                + " date "
                + court_config["check_date"].strftime("%d.%m.%Y")
                + " failed."
            )
            failed += 1
        while True:
            try:
                db_tools.log_scrapped_court(
                    db_config, court_config["alias"], court_config["check_date"], status
                )
                break
            except Exception as elog:
                logger.warning(
                    "Failed to load log entry. Retry in 5 seconds - " + str(elog)
                )
                time.sleep(5)


def parse_args() -> argparse.Namespace:
    """Parser for command-line options, arguments and sub-commands."""

    parser = argparse.ArgumentParser(
        prog="Courts Info Scraper",
        description="Scraps courts info",
    )
    parser.add_argument(
        "--start_date", help="Date to parse from, format YYYY-MM-DD", type=str
    )
    parser.add_argument("--end_date", help="Date to parse to, YYYY-MM-DD", type=str)
    parser.add_argument(
        "--retry",
        help="Retry mode - only failed steps from last load will be triggered",
        type=bool,
        default=False,
    )
    parser.add_argument("--env", help="Environment name", type=str, choices=["dev", "prod"], default="dev")
    parsed_args = parser.parse_args()

    return parsed_args


def main() -> None:
    """main class"""
    # add file logger
    log_file_name = "../log/" + datetime.now().strftime(
        "scrap_cases_to_db_%Y-%m-%d_%H%M%S.log"
    )
    logger.add(sys.stderr, level="DEBUG")
    logger.add(log_file_name, encoding="utf-8", retention="7 days")

    args = parse_args()

    # Load environment variables from .env_hosting file from the project root dir
    load_dotenv(dotenv_path=f".env_{args.env}")
    db_config_wrk = {
        "host": os.environ["MYSQL_HOST_WRK"],
        "port": os.environ["MYSQL_PORT_WRK"],
        "user": os.environ["MYSQL_USER_WRK"],
        "passwd": os.environ["MYSQL_PASS_WRK"],
        "db": os.environ["MYSQL_DB_WRK"],
        "engine_type": "mysql",
    }

    courts_config = db_tools.read_courts_config(
        db_config=db_config_wrk,
        in_start_date=args.start_date,
        in_end_date=args.end_date,
        retry=args.retry,
    )

    scrap_courts(courts_config, db_config_wrk)
    # scrap_courts_no_parallel(courts_config, db_config_wrk)

    db_tools.etl_load_court_cases_dq(db_config_wrk)
    db_tools.etl_load_court_cases_dv(db_config_wrk)
    db_tools.etl_load_court_cases_dm(db_config_wrk)

    # db_tools.transfer_dm_from_wrk_to_host(
    #    db_config_wrk, db_config, scraper_config.DM_COURT_CASES_TABLES_TO_TRANSFER
    # )
    db_tools.switch_dm_tables(
       db_config_wrk, db_config_wrk, scraper_config.DM_COURT_CASES_TABLES_TO_TRANSFER
    )
    db_tools.deactivate_outdated_bot_log_entries(db_config_wrk)
    db_tools.clean_stage_courts_table(db_config_wrk)


if __name__ == "__main__":
    main()
