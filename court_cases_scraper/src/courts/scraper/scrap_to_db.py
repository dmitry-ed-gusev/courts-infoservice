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
                                                    parser_7)
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

logger.remove()
# setup for multithreading processing
thread_local = threading.local()  # thread local storage


def thread_count(futures: list[Future]) -> tuple[int, int]:
    """count running threads"""
    running = 0
    done = 0
    for future in futures:
        if future.running():
            running += 1
        if future.done():
            running += 1
    return running, done


def threadsafe_function(fn):
    """Decorator making sure that the decorated function is thread safe."""
    lock = threading.Lock()

    def new(*args, **kwargs):
        lock.acquire()
        try:
            r = fn(*args, **kwargs)
        # except Exception as e:
        #     raise e
        finally:
            lock.release()
        return r

    return new


def scrap_courts_no_parallel(courts_config: list[dict[str, str]], db_config: dict[str, str]):
    """router with parallel execution"""

    for idx, court in enumerate(courts_config):
        logger.info("Processing " + court.get("alias") + " date " + court.get("check_date").strftime(
            "%d.%m.%Y") + " with parser " + court.get("parser_type") + ", " + str(
            idx + 1) + "/" + str(len(courts_config)))
        if court.get("parser_type") == "1":
            result_part, court_config, mapping = parser_1.parse_page(court)
        elif court.get("parser_type") == "2":
            result_part, court_config, mapping = parser_2.parse_page(court)
        elif court.get("parser_type") == "3":
            result_part, court_config, mapping = parser_3.parse_page(court)
        elif court.get("parser_type") == "4":
            result_part, court_config, mapping = parser_4.parse_page(court)
        elif court.get("parser_type") == "5":
            result_part, court_config, mapping = parser_5.parse_page(court)
        elif court.get("parser_type") == "6":
            result_part, court_config, mapping = parser_6.parse_page(court)
        elif court.get("parser_type") == "7":
            result_part, court_config, mapping = parser_7.parse_page(court)
        else:
            continue
        result_len = len(result_part)
        if result_len > 0:
            db_tools.load_to_stage(result_part, mapping, db_config, court_config.get("alias"),
                                   court_config.get("check_date"))
            db_tools.load_to_dm(db_config, court_config.get("alias"), court_config.get("check_date"))
        logger.info("Parser " + court_config.get("parser_type") + " court " + court_config.get(
            "alias") + " date " + court_config.get("check_date").strftime(
            "%d.%m.%Y") + " loaded. Total records " + str(result_len))
        db_tools.log_scrapped_court(db_config, court_config.get("alias"), court_config.get("check_date"))


@threadsafe_function
def scrap_courts(courts_config: list[dict[str, str]], db_config: dict[str, str]):
    """router with parallel execution"""
    futures = []  # list to store future results of threads
    with (
        ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_1) as executor1,
        ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_2) as executor2,
        ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_3) as executor3,
        ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_4) as executor4,
        ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_5) as executor5,
        ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_6) as executor6,
        ThreadPoolExecutor(max_workers=config.WORKERS_COUNT_7) as executor7,
    ):
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

        for task in as_completed(futures):
            running, done = thread_count(futures)
            logger.debug(f"{done} completed. {running} running threads remaining.")
            result_part, court_config, mapping = task.result()
            result_len = len(result_part)
            if result_len > 0:
                db_tools.load_to_stage(result_part, mapping, db_config, court_config.get("alias"),
                                       court_config.get("check_date"))
                db_tools.load_to_dm(db_config, court_config.get("alias"), court_config.get("check_date"))
            logger.info("Parser " + court_config.get("parser_type") + " court " + court_config.get(
                "alias") + " date " + court_config.get("check_date").strftime(
                "%d.%m.%Y") + " loaded. Total records " + str(result_len))
            db_tools.log_scrapped_court(db_config, court_config.get("alias"), court_config.get("check_date"))


def main() -> None:
    """main class"""
    # add file logger
    log_file_name = "../log/" + datetime.now().strftime("scrap_to_db_%Y-%m-%d_%H%M%S.log")
    logger.add(sys.stderr, level="DEBUG")
    logger.add(log_file_name, encoding="utf-8")

    # Load environment variables from .env_hosting file from the project root dir
    load_dotenv()
    db_config = {"host": os.environ["MYSQL_HOST"],
                 "port": os.environ["MYSQL_PORT"],
                 "user": os.environ["MYSQL_USER"],
                 "passwd": os.environ["MYSQL_PASS"],
                 "db": os.environ["MYSQL_DB"]
                 }
    courts_config = db_tools.read_courts_config(db_config)
    scrap_courts(courts_config, db_config)
    # scrap_courts_no_parallel(courts_config, db_config)


if __name__ == "__main__":
    main()
