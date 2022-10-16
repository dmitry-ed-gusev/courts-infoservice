"""scrap regular court pages from sudrf"""
from bs4 import BeautifulSoup
from loguru import logger
from pandas import DataFrame
import time
import random

from courts.config import scraper_config as config
from courts.db.db_tools import convert_data_to_df
from courts.web.web_client import WebClient


def parse_page(court: dict) -> tuple[DataFrame, dict]:
    """parses output page"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    session = WebClient()
    session.headers = {"user-agent": config.USER_AGENT}
    url = court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get("server_num") + "&H_date=" + check_date
    logger.debug(url)
    time.sleep(random.randrange(0, 3))
    page = session.get(url)
    result = []
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("div", id="tablcont")
    # <div id="tablcont">
    for table in tables:
        section_name = ""
        sections = table.find_all("tr")
        # tr
        for idx, section in enumerate(sections):
            if idx == 0:
                continue
            # setting new section
            if len(section.contents) == 1:
                for idx_r, row in enumerate(section.find_all("td")):
                    section_name = row.text
            # appending row
            else:
                result_row = {"section_name": section_name}
                # td
                for idx_r, row in enumerate(section.find_all("td")):
                    if row.text:
                        result_row["col" + str(idx_r)] = row.text.strip()
                    else:
                        result_row["col" + str(idx_r)] = str(row.contents).strip()
                    if row.find(href=True):
                        result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result_row["court_alias"] = court.get("alias")
                result.append(result_row)
    data_frame = convert_data_to_df(result, config.STAGE_MAPPING_1)
    return data_frame, court
