"""
parse court data and load to stage
"""
import os
from dotenv import load_dotenv
from loguru import logger
from court_cases_scraper.src.courts.db import db_tools
from court_cases_scraper.src.courts.scraper import parser_1, parser_2, parser_3, parser_4, parser_5, parser_6


def scrap_courts(courts_config: list[dict[str, str]],  db_config: dict[str, str]):

    for idx, court in enumerate(courts_config):
        logger.info("Processing " + court.get("alias") + " with parser " + court.get("parser_type") + ", " + str(
            idx + 1) + "/" + str(len(courts_config)))
        if court.get("parser_type") == "1":
            parser_1.parser_type_1(court, db_config)
        elif court.get("parser_type") == "2":
            parser_2.parser_type_2(court, db_config)
        elif court.get("parser_type") == "3":
            parser_3.parser_type_3(court, db_config)
        elif court.get("parser_type") == "4":
            parser_4.parser_type_4(court, db_config)
        elif court.get("parser_type") == "5":
            parser_5.parser_type_5(court, db_config)
        elif court.get("parser_type") == "6":
            parser_6.parser_type_6(court, db_config)

def main() -> None:
    # Load environment variables from .env file from the project root dir
    load_dotenv()
    db_config = {"host": os.environ["MYSQL_HOST"],
                 "port": os.environ["MYSQL_PORT"],
                 "user": os.environ["MYSQL_USER"],
                 "passwd": os.environ["MYSQL_PASS"]}
    courts_config = db_tools.read_courts_config(db_config)
    scrap_courts(courts_config, db_config)


if __name__ == "__main__":
    main()
