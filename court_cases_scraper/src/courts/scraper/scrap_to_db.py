"""
parse court data and load to stage
"""
import os
import sys
import threading

from dotenv import load_dotenv
from datetime import datetime
from loguru import logger
from courts.db import db_tools
from courts.config import scraper_config as config
from courts.scraper import (parser_1, parser_2, parser_3, parser_4, parser_5, parser_6,
                            parser_7, parser_8)
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

logger.remove()
# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def thread_count(futures: list[Future]) -> tuple[int, int, int]:
    """count running threads"""
    running = 0
    done = 0
    cancelled = 0
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
        if court.get("parser_type") == "1":
            result_part, court_config, status = parser_1.parse_page(court)
        elif court.get("parser_type") == "2":
            result_part, court_config, status = parser_2.parse_page(court)
        elif court.get("parser_type") == "3":
            result_part, court_config, status = parser_3.parse_page(court)
        elif court.get("parser_type") == "4":
            result_part, court_config, status = parser_4.parse_page(court)
        elif court.get("parser_type") == "9":
            result_part, court_config, status = parser_5.parse_page(court)
        elif court.get("parser_type") == "6":
            result_part, court_config, status = parser_6.parse_page(court)
        elif court.get("parser_type") == "7":
            result_part, court_config, status = parser_7.parse_page(court)
        elif court.get("parser_type") == "8":
            result_part, court_config, status = parser_8.parse_page(court)
        else:
            continue
        result_len = len(result_part)
        if result_len > 0:
            db_tools.load_to_stage_alchemy(result_part, db_config)
            db_tools.load_to_dm(db_config, court_config["alias"], court_config["check_date"])
        if status == "success":
            logger.info("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " loaded. Total records " + str(result_len))
        elif status == "failure":
            logger.warning("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " failed.")
        db_tools.log_scrapped_court(db_config, court_config["alias"], court_config["check_date"], status)


@config.threadsafe_function
def scrap_courts(courts_config: list[dict[str, str | datetime]], db_config: dict[str, str]):
    """router with parallel execution"""
    futures = []  # list to store future results of threads
    executor1 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_1)
    executor2 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_2)
    executor3 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_3)
    executor4 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_4)
    executor5 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_5)
    executor6 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_6)
    executor7 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_7)
    executor8 = ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_8)
    for idx, court in enumerate(courts_config):
        if court.get("parser_type") == "1":
            future = executor1.submit(parser_1.parse_page, court)
            futures.append(future)
        elif court.get("parser_type") == "2":
            future = executor2.submit(parser_2.parse_page, court)
            futures.append(future)
        elif court.get("parser_type") == "3":
            future = executor3.submit(parser_3.parse_page, court)
            futures.append(future)
        elif court.get("parser_type") == "4":
            future = executor4.submit(parser_4.parse_page, court)
            futures.append(future)
        elif court.get("parser_type") == "5":
            future = executor5.submit(parser_5.parse_page, court)
            futures.append(future)
        elif court.get("parser_type") == "6":
            future = executor6.submit(parser_6.parse_page, court)
            futures.append(future)
        elif court.get("parser_type") == "7":
            future = executor7.submit(parser_7.parse_page, court)
            futures.append(future)
        elif court.get("parser_type") == "8":
            future = executor8.submit(parser_8.parse_page, court)
            futures.append(future)
    loaded = 0
    for task in as_completed(futures):
        running, done, total = thread_count(futures)
        logger.info(
            f"{running} running. {done} completed. {loaded} loaded. Total {total}. " + str(round(done/total*100, 2)) + "%")
        result_part, court_config, status = task.result()
        result_len = len(result_part)
        if result_len > 0:
            db_tools.load_to_stage_alchemy(result_part, db_config)
            db_tools.load_to_dm(db_config, court_config["alias"], court_config["check_date"])
        if status == "success":
            logger.info("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " loaded. Total records " + str(result_len))
        elif status == "failure":
            logger.warning("Parser " + court_config["parser_type"] + " court " + court_config[
                "alias"] + " date " + court_config["check_date"].strftime(
                "%d.%m.%Y") + " failed.")
        db_tools.log_scrapped_court(db_config, court_config["alias"], court_config["check_date"], status)
        loaded += 1


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
    db_tools.clean_stage_table(db_config)
    scrap_courts(courts_config, db_config)
    # scrap_courts_no_parallel(courts_config, db_config)


if __name__ == "__main__":
    main()
