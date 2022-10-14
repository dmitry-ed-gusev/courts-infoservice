"""scrap regular court pages from sudrf"""
import time
import requests
from bs4 import BeautifulSoup
from loguru import logger

from court_cases_scraper.src.courts.config import scraper_config as config


def parse_page(court: dict) -> tuple[list[dict[str, str]], dict, list[dict[str, str]]]:
    """parses output page"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    session = requests.Session()
    session.headers = {"user-agent": config.USER_AGENT}
    url = court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get("server_num") + "&H_date=" + check_date
    logger.debug(url)
    retries = 0
    page = session.get(url)
    while page.status_code != 200:
        time.sleep(2)
        page = session.get(url)
        retries += 1
        if retries > config.MAX_RETRIES:
            break
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
    return result, court, config.STAGE_MAPPING_1
