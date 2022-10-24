"""scrap moscow mir courts"""
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import re
import random
import time
from bs4 import BeautifulSoup
from loguru import logger
from pandas import DataFrame

from courts.config import scraper_config
from court_cases_scraper.src.courts.config import selenium_config
from courts.db.db_tools import convert_data_to_df


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """parses mos sud page with paging"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    while True:
        try:
            firefox_service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=firefox_service,
                                       options=selenium_config.firefox_options)
            break
        except:
            time.sleep(3)
    result = []
    page_num = 1
    pages_total = 1
    order_num = 0
    time.sleep(1)
    while True:
        url = court.get(
            "link") + "/hearing?hearingRangeDateFrom=" + check_date + "&hearingRangeDateTo=" + check_date + "&page=" + str(
            page_num)
        retries = 0
        while True:
            retries += 1
            time.sleep(random.randrange(0, 3))
            if retries > 4:
                return DataFrame(), court, "failure"
            try:
                driver.get(url)
                html = driver.page_source
                break
            except:
                None
        soup = BeautifulSoup(html, "html.parser")
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
                    order_num += 1
                    # td
                    for idx_r, row in enumerate(section.find_all("td")):
                        if idx_r == 2:
                            result_row["hearing_time"] = row.text.strip()[10:].strip()
                        else:
                            value = row.text.strip().replace("\n", " ").replace("\t", " ")
                            value = re.sub("\s+", " ", value)[:10000]
                            result_row["col" + str(idx_r)] = value
                            if row.find(href=True):
                                result_row["col" + str(idx_r) + "_link"] = "https://mos-sud.ru" + row.find(href=True)[
                                    "href"]

                    result_row["check_date"] = check_date
                    result_row["court"] = court.get("title")
                    result_row["court_alias"] = court.get("alias")
                    result_row["order_num"] = order_num
                    result.append(result_row)
        if page_num == 1:
            try:
                pages_total = int(soup.find("input", id="paginationFormMaxPages").attrs["value"])
            except:
                None
        logger.debug(driver.current_url + ", pages " + str(pages_total))
        if page_num < pages_total:
            page_num += 1
        else:
            break
        # closes 10 windows and open new driver
        if page_num % 10 == 0:
            driver.close()
            while True:
                try:
                    driver = webdriver.Firefox(service=firefox_service,
                                               options=selenium_config.firefox_options)
                    break
                except:
                    time.sleep(3)

    driver.close()
    data_frame = convert_data_to_df(result, scraper_config.SCRAPER_CONFIG[5]["stage_mapping"])
    return data_frame, court, "success"

