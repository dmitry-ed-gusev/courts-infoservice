"""scrap regular court pages from sudrf"""
import random
import time

from bs4 import BeautifulSoup
from courts.config import scraper_config
from courts.db.db_tools import convert_data_to_df
from courts.web.web_client import WebClient
from loguru import logger
from pandas import DataFrame


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """parses output page"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    session = WebClient()
    session.headers = {"user-agent": scraper_config.USER_AGENT}
    url = (
        court.get("link")
        + "/modules.php?name=sud_delo&srv_num="
        + court.get("server_num")
        + "&H_date="
        + check_date
    )
    logger.debug(url)
    time.sleep(random.randrange(0, 3))
    try:
        page = session.get(url)
    except:
        return DataFrame(), court, "failure"
    result = []
    soup = BeautifulSoup(page.content, "html.parser")
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
                        result_row["col" + str(idx_r) + "_link"] = (
                            court.get("link") + row.find(href=True)["href"]
                        )

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result_row["court_alias"] = court.get("alias")
                result.append(result_row)
    data_frame = convert_data_to_df(
        result, scraper_config.SCRAPER_CONFIG[1]["stage_mapping"]
    )
    return data_frame, court, "success"


def get_links(link_config: dict) -> tuple[DataFrame, dict, str]:
    """extracts linked cases and case_uid"""
    session = WebClient()
    logger.debug(link_config["case_link"])
    try:
        page = session.get(link_config["case_link"])
    except:
        return DataFrame(), link_config, "failure"
    soup = BeautifulSoup(page.content, "html.parser")
    rows = soup.find_all("tr")
    case_uid = link_case_num = link_court_name = None
    for row in rows:
        cols = row.find_all("td")
        if len(cols) != 2:
            continue
        if cols[0].text.strip() == "Уникальный идентификатор дела":
            case_uid = cols[1].text.strip()
        if cols[0].text.strip() == "Номер дела в первой инстанции":
            link_case_num = cols[1].text.strip()
        if cols[0].text.strip() == "Суд (судебный участок) первой инстанции":
            link_court_name = cols[1].text.strip()
    data = {
        "case_link": [
            link_config["case_link"],
        ],
        "court_alias": [
            link_config["alias"],
        ],
        "case_num": [
            link_config["case_num"],
        ],
        "case_uid": [
            case_uid,
        ],
        "link_case_num": [
            link_case_num,
        ],
        "link_court_name": [
            link_court_name,
        ],
        "link_level": [
            "1",
        ],
        "is_primary": [
            True,
        ],
    }
    result = DataFrame(data)
    return result, link_config, "success"
