"""
parse court data and load to stage
"""
import os
import sys
import time
import threading

from dotenv import load_dotenv
from datetime import datetime
from loguru import logger
from courts.db import db_tools
from courts.config.scraper_config import SCRAPER_CONFIG
from courts.scraper import (parser_1, parser_2, parser_3, parser_4, parser_5, parser_6,
                            parser_7, parser_8, parser_9)
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from courts.utils.utilities import threadsafe_function

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


def scrap_courts_no_parallel(courts_config: list[dict[str, str | datetime]], db_config: dict[str, str]):
    """router with parallel execution"""

    for idx, court in enumerate(courts_config):
        logger.info("Processing " + court["alias"] + " date " + court["check_date"].strftime(
            "%d.%m.%Y") + " with parser " + court["parser_type"] + ", " + str(
            idx + 1) + "/" + str(len(courts_config)))
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
            db_tools.load_courts_to_stage(result_part, db_config)
            db_tools.load_courts_to_dm(db_config, court_config["alias"], court_config["check_date"])
        if status == "success":
            logger.info("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " loaded. Total records " + str(result_len))
        elif status == "failure":
            logger.warning("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " failed.")
        db_tools.log_scrapped_court(db_config, court_config["alias"], court_config["check_date"], status)


@threadsafe_function
def scrap_courts(courts_config: list[dict[str, str | datetime]], db_config: dict[str, str]):
    """router with parallel execution"""
    futures = []  # list to store future results of threads
    executor1 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[1]["workers_count"])
    executor2 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[2]["workers_count"])
    executor3 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[3]["workers_count"])
    executor4 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[4]["workers_count"])
    executor5 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[5]["workers_count"])
    executor6 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[6]["workers_count"])
    executor7 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[7]["workers_count"])
    executor8 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[8]["workers_count"])
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
            future = executor8.submit(parser_9.parse_page, court)
        else:
            continue
        futures.append(future)
    loaded = 0
    failed = 0
    for task in as_completed(futures):
        running, done, total = thread_count(futures)
        logger.info(
            f"{running} running. {done} completed. {loaded} loaded. {failed} failed. Total {total}. " + str(
                round(done / total * 100, 2)) + "% scrapped. " + str(
                round(loaded / (total - failed) * 100, 2)) + "% loaded.")
        try:
            result_part, court_config, status = task.result()
        except Exception as ue:
            logger.warning("Unexpected error in one of the workers. Skipping. Error:\n" + str(ue))
            failed += 1
            continue
        result_len = len(result_part)
        if result_len > 0:
            while True:
                try:
                    db_tools.load_courts_to_stage(result_part, db_config)
                    break
                except Exception as estg:
                    logger.warning("Failed to load data to stage. Retry in 3 seconds - " + str(estg))
                    time.sleep(3)
            while True:
                try:
                    db_tools.load_courts_to_dm(db_config, court_config["alias"], court_config["check_date"])
                    break
                except Exception as edm:
                    logger.warning("Failed to load data to dm. Retry in 3 seconds - " + str(edm))
                    time.sleep(3)
        if status == "success":
            logger.info("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " loaded. Total records " + str(result_len))
            loaded += 1
        elif status == "failure":
            logger.warning("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " failed.")
            failed += 1
        while True:
            try:
                db_tools.log_scrapped_court(db_config, court_config["alias"], court_config["check_date"], status)
                break
            except Exception as elog:
                logger.warning("Failed to load log entry. Retry in 3 seconds - " + str(elog))
                time.sleep(3)


def main() -> None:
    """main class"""
    # add file logger
    log_file_name = "../log/" + datetime.now().strftime("scrap_to_db_%Y-%m-%d_%H%M%S.log")
    logger.add(sys.stderr, level="DEBUG")
    logger.add(log_file_name, encoding="utf-8", retention="7 days")

    # Load environment variables from .env_hosting file from the project root dir
    load_dotenv()
    db_config = {"host": os.environ["MYSQL_HOST"],
                 "port": os.environ["MYSQL_PORT"],
                 "user": os.environ["MYSQL_USER"],
                 "passwd": os.environ["MYSQL_PASS"],
                 "db": os.environ["MYSQL_DB"]
                 }
    courts_config = db_tools.read_courts_config(db_config)
    db_tools.clean_stage_courts_table(db_config)
    scrap_courts(courts_config, db_config)
    # scrap_courts_no_parallel(courts_config, db_config)


if __name__ == "__main__":
    main()
