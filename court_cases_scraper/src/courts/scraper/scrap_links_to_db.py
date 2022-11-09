"""
parse court data and load to stage
"""
import os
import sys
import time
import threading

from pandas import DataFrame, concat
from dotenv import load_dotenv
from datetime import datetime
from loguru import logger
from courts.db import db_tools
from courts.config.scraper_config import SCRAPER_CONFIG
from courts.scraper import parser_1, parser_2, parser_3, parser_4, parser_5, parser_6, parser_8
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


def scrap_links_no_parallel(links_config: list[dict[str, str | datetime]], db_config: dict[str, str]):
    """router with parallel execution"""
    result = DataFrame()
    for idx, link_config in enumerate(links_config):
        logger.info("Processing " + link_config["case_link"] + ", " + link_config["parser_type"] + ", " + str(
            idx + 1) + "/" + str(len(links_config)))
        if link_config["parser_type"] == "1":
            result_part, _, status = parser_1.get_links(link_config)
        elif link_config["parser_type"] == "2":
            result_part, _, status = parser_2.get_links(link_config)
        elif link_config["parser_type"] == "3":
            result_part, _, status = parser_3.get_links(link_config)
        elif link_config["parser_type"] == "4":
            result_part, _, status = parser_4.get_links(link_config)
        elif link_config["parser_type"] == "5":
            result_part, _, status = parser_5.get_links(link_config)
        elif link_config["parser_type"] == "6":
            result_part, _, status = parser_6.get_links(link_config)
        elif link_config["parser_type"] == "8":
            result_part, _, status = parser_8.get_links(link_config)
        else:
            continue
        result = concat([result, result_part], ignore_index=True)
    db_tools.load_links_to_stage(result, db_config)
    db_tools.load_links_to_dm(db_config)


@threadsafe_function
def scrap_links(links_config: list[dict[str, str | datetime]], db_config: dict[str, str]):
    """router with parallel execution"""
    futures = []  # list to store future results of threads
    executor1 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[1]["workers_count"])
    executor2 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[2]["workers_count"])
    executor3 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[3]["workers_count"] * 2)
    executor4 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[4]["workers_count"])
    executor5 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[5]["workers_count"])
    executor6 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[6]["workers_count"])
    executor8 = ThreadPoolExecutor(max_workers=SCRAPER_CONFIG[8]["workers_count"] * 2)
    for link_config in links_config:
        if link_config["parser_type"] == "1":
            future = executor1.submit(parser_1.get_links, link_config)
        elif link_config["parser_type"] == "2":
            future = executor2.submit(parser_2.get_links, link_config)
        elif link_config["parser_type"] == "3":
            future = executor3.submit(parser_3.get_links, link_config)
        elif link_config["parser_type"] == "4":
            future = executor4.submit(parser_4.get_links, link_config)
        elif link_config["parser_type"] == "5":
            future = executor5.submit(parser_5.get_links, link_config)
        elif link_config["parser_type"] == "6":
            future = executor6.submit(parser_6.get_links, link_config)
        elif link_config["parser_type"] == "8":
            future = executor8.submit(parser_8.get_links, link_config)
        else:
            continue
        futures.append(future)
    failed = 0
    result = DataFrame()
    for task in as_completed(futures):
        running, done, total = thread_count(futures)
        logger.info(
            f"{running} running. {done} completed. {failed} failed. Total {total}. " + str(
                round(done / total * 100, 2)) + "% scrapped. Temp result size " + str(len(result)) + ".")
        try:
            result_part, link_config, status = task.result()
        except Exception as ue:
            logger.warning("Unexpected error in one of the workers. Skipping. Error:\n" + str(ue))
            failed += 1
            continue

        if len(result_part) == 0:
            logger.warning("No data from " + link_config["case_link"])
            continue

        result = concat([result, result_part], ignore_index=True)
        # load each 1000 records from result
        if len(result) > 1000:
            while True:
                try:
                    db_tools.load_links_to_stage(result, db_config)
                    break
                except Exception as estg:
                    logger.warning("Failed to load data to stage. Retry in 3 seconds - " + str(estg))
                    time.sleep(3)
            while True:
                try:
                    db_tools.load_links_to_dm(db_config)
                    break
                except Exception as edm:
                    logger.warning("Failed to load data to dm. Retry in 3 seconds - " + str(edm))
                    time.sleep(3)
            result = DataFrame()

    # final load when all runners completed
    while True:
        try:
            db_tools.load_links_to_stage(result, db_config)
            break
        except Exception as estg:
            logger.warning("Failed to load data to stage. Retry in 3 seconds - " + str(estg))
            time.sleep(3)
    while True:
        try:
            db_tools.load_links_to_dm(db_config)
            break
        except Exception as edm:
            logger.warning("Failed to load data to dm. Retry in 3 seconds - " + str(edm))
            time.sleep(3)


def main() -> None:
    """main class"""
    # add file logger
    log_file_name = "../log/" + datetime.now().strftime("scrap_links_to_db_%Y-%m-%d_%H%M%S.log")
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
    for i in range(1, 10):
        links_config = db_tools.read_links_config(db_config)
        db_tools.clean_stage_links_table(db_config)
        scrap_links(links_config, db_config)
    # scrap_links_no_parallel(links_config, db_config)


if __name__ == "__main__":
    main()
