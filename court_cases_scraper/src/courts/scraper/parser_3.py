"""scrap js page of krasnodarskiy kraevoy sud"""
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from loguru import logger
from pandas import DataFrame

from courts.config import scraper_config as config
from court_cases_scraper.src.courts.config import selenium_config
from courts.db.db_tools import convert_data_to_df


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """parses output js page"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    result = []
    while True:
        try:
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),
                                       options=selenium_config.firefox_options)
            break
        except:
            time.sleep(3)
    url = court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get("server_num") + "&H_date=" + check_date
    logger.debug(url)
    retries = 0
    while True:
        time.sleep(random.randrange(0, 3))
        retries += 1
        if retries > 4:
            return DataFrame(), court, "failure"
        try:
            driver.get(url)
            break
        except:
            None
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("div", id="resultTable")
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
                        result_row["col" + str(idx_r)] = row.text.strip()
                    else:
                        result_row["col" + str(idx_r)] = str(row.contents).strip()
                    if row.find(href=True):
                        result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]

                result_row["check_date"] = check_date
                result_row["court"] = court.get("title")
                result_row["court_alias"] = court.get("alias")
                result.append(result_row)
    driver.close()
    data_frame = convert_data_to_df(result, config.STAGE_MAPPING_3)
    return data_frame, court, "success"
