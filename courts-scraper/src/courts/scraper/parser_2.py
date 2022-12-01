"""scrap moscow regular courts"""
import random
import re
import time

from bs4 import BeautifulSoup
from courts.config import scraper_config
from courts.db.db_tools import convert_data_to_df
from courts.web.web_client import WebClient
from loguru import logger
from pandas import DataFrame


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """parses mos gor sud page with paging"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    session = WebClient()
    session.headers = {"user-agent": scraper_config.USER_AGENT}
    result = []
    page_num = 1
    pages_total = 1
    while True:
        url = (
            court.get("link")
            + "&hearingRangeDateFrom="
            + check_date
            + "&hearingRangeDateTo="
            + check_date
            + "&page="
            + str(page_num)
        )
        time.sleep(random.randrange(1, 3))
        try:
            page = session.get(url)
        except:
            return DataFrame(), court, "failure"
        soup = BeautifulSoup(page.content, "html.parser")
        tables = soup.find_all("div", class_="wrapper-search-tables")
        # <div class="wrapper-search-tables">
        for table in tables:
            sections = table.find_all("tr")
            # tr
            for idx, section in enumerate(sections):
                # skip header
                if idx == 0:
                    continue
                # appending row
                else:
                    result_row = {}
                    # td
                    for idx_r, row in enumerate(section.find_all("td")):
                        if idx_r == 3:
                            result_row["hearing_time"] = row.text.strip()[10:].strip()
                        else:
                            value = (
                                row.text.strip().replace("\n", " ").replace("\t", " ")
                            )
                            value = re.sub("\s+", " ", value)[:10000]
                            result_row["col" + str(idx_r)] = value
                            if row.find(href=True):
                                result_row["col" + str(idx_r) + "_link"] = (
                                    "https://mos-gorsud.ru"
                                    + row.find(href=True)["href"]
                                )

                    result_row["check_date"] = check_date
                    result_row["court"] = court.get("title")
                    result_row["court_alias"] = court.get("alias")
                    result.append(result_row)
        if page_num == 1:
            try:
                pages_total = int(
                    soup.find("input", id="paginationFormMaxPages").attrs["value"]
                )
            except:
                None
        logger.debug(str(page.url) + ", pages " + str(pages_total))
        if page_num < pages_total:
            page_num += 1
        else:
            break
    data_frame = convert_data_to_df(
        result, scraper_config.SCRAPER_CONFIG[2]["stage_mapping"]
    )
    return data_frame, court, "success"


def get_links(link_config: dict) -> tuple[DataFrame, dict, str]:
    """extracts linked cases and case_uid"""
    session = WebClient(
        dont_raise_for=[
            404,
        ]
    )
    session.headers = {"user-agent": scraper_config.USER_AGENT}
    logger.debug(link_config["case_link"])
    time.sleep(1)
    try:
        page = session.get(link_config["case_link"])
    except Exception as e:
        return DataFrame(), link_config, "failure"

    soup = BeautifulSoup(page.content, "html.parser")
    rows = soup.find_all("div", class_="row_card")
    case_uid = None
    for row in rows:
        cols = row.find_all("div")
        if len(cols) != 2:
            continue
        if cols[0].text.strip() == "Уникальный идентификатор дела":
            case_uid = cols[1].text.strip()
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
    }
    result = DataFrame(data)
    return result, link_config, "success"
