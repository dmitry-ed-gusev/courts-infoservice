"""scrap js page of len obl sud"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time
import random
from loguru import logger
from pandas import DataFrame

from courts.config import scraper_config, selenium_config
from courts.db.db_tools import convert_data_to_df
from courts.web.web_client import WebClient


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """parses output js page"""
    result = []
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    firefox_service = Service(GeckoDriverManager(version=selenium_config.gecko_version).install())
    while True:
        try:
            driver = webdriver.Firefox(service=firefox_service,
                                       options=selenium_config.firefox_options)
            break
        except:
            time.sleep(3)
    driver.set_page_load_timeout(scraper_config.PAGE_LOAD_TIMEOUT)
    url = court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get("server_num") + "&H_date=" + check_date
    logger.debug(url)
    retries = 0
    while True:
        time.sleep(random.randrange(0, 3))
        retries += 1
        if retries > 4:
            driver.close()
            driver.quit()
            return DataFrame(), court, "failure"
        try:
            driver.get(url)
            break
        except:
            None
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("div", id="tablcont")
    # <div id="resultTable">
    for table in tables:
        section_name = ""
        sections = table.find_all("tr")
        # tr
        for idx, section in enumerate(sections):
            if idx == 0:
                continue
            # setting new section
            if len(section.find_all("td")) == 1:
                for idx_r, row in enumerate(section.find_all("td")):
                    section_name = row.text.title()
            # appending row
            else:
                result_row = {"section_name": section_name}
                # td
                for idx_r, row in enumerate(section.find_all("td")):
                    if row.text:
                        result_row["col" + str(idx_r)] = row.text.replace("БЕЗ ИМЕНИ!", "").strip()
                    else:
                        result_row["col" + str(idx_r)] = str(row.contents).strip()
                    if row.find(href=True):
                        result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result_row["court_alias"] = court.get("alias")
                result.append(result_row)
    driver.close()
    driver.quit()
    data_frame = convert_data_to_df(result, scraper_config.SCRAPER_CONFIG[6]["stage_mapping"])
    return data_frame, court, "success"


def get_links(link_config: dict) -> tuple[DataFrame, dict, str]:
    """extracts linked cases and case_uid"""
    session = WebClient()
    logger.debug(link_config["case_link"])
    try:
        page = session.get(link_config["case_link"])
    except:
        return DataFrame(), link_config, "failure"

    soup = BeautifulSoup(page.content, 'html.parser')
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
    data = {"case_link": [link_config["case_link"], ],
            "court_alias": [link_config["alias"], ],
            "case_num": [link_config["case_num"], ],
            "case_uid": [case_uid, ],
            "link_case_num": [link_case_num, ],
            "link_court_name": [link_court_name, ],
            "link_level": ["1", ],
            "is_primary": [True, ],
            }
    result = DataFrame(data)
    return result, link_config, "success"
