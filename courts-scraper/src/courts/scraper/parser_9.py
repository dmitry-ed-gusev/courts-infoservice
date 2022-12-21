"""scrap vsrf ru"""
import re
import time

from bs4 import BeautifulSoup
from courts.config import scraper_config, selenium_config
from courts.db.db_tools import convert_data_to_df
from courts.web.web_client import WebClient
from loguru import logger
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """request page and parse response"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    result = []
    section_name = ""
    firefox_service = Service(
        GeckoDriverManager(version=selenium_config.gecko_version).install()
    )
    while True:
        try:
            driver = webdriver.Firefox(
                service=firefox_service, options=selenium_config.firefox_options
            )
            break
        except:
            time.sleep(3)
    driver.set_page_load_timeout(scraper_config.PAGE_LOAD_TIMEOUT)
    url = (
        court.get("link")
        + "/lk/practice/hearings?&numberExact=true&eventDateExact=true&eventDateFrom="
        + check_date
    )
    logger.debug(url)
    retries = 0
    while True:
        retries += 1
        if retries > 4:
            driver.close()
            return DataFrame(), court, "failure"
        try:
            driver.get(url)
            break
        except:
            None
    retries = 0
    while True:
        retries += 1
        if retries > 10:
            driver.close()
            return DataFrame(), court, "failure"
        try:
            button = driver.find_element("id", "loadButtonContainer")
            button.click()
            time.sleep(2)
        except Exception as button_e:
            break

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("div", id="vs-search-items")
    # <div id="vs-search-items">
    for table in tables:
        items = table.find_all("div", class_="vs-items-body")
        for item in items:
            skip = False
            result_row = {}
            case_info = ""
            # section_name
            for section in item.find_all(
                "div", attrs={"data-mark-from-name": "departmentId"}
            ):
                section_name = section.text.strip()
            # case_num and case_link
            for case_number in item.find_all(
                "div", class_="col-md-3 col-sm-3 col-xs-3 vs-items-label"
            ):
                result_row["case_num"] = case_number.text.strip()
                for link in case_number.find_all("a"):
                    if str(link["href"]).startswith("/lk"):
                        result_row["case_link"] = court.get("link") + link["href"]
                    else:
                        skip = True
            # skip rows from kad.arbitr.ru
            if skip:
                continue

            rows = item.find_all("div", class_="row vs-item-detail")
            # case info and hearing result
            for row in rows:
                if row.find("div", class_="col-md-2") or row.find(
                    "div", class_="col-md-offset-2 col-md-3 col-sm-3 col-xs-3"
                ):
                    case_info += row.text.strip().replace("\n", " ") + ". "
                if row.find("div", class_="col-md-offset-4 col-md-1 padding-r-0"):
                    result_row["hearing_result"] = row.text.strip()

            # hearing place
            for hearing_place in item.find_all(
                "div", class_="col-md-7 col-sm-7 col-xs-7 vs-items-title"
            ):
                result_row["hearing_place"] = re.sub(
                    "\s+", " ", hearing_place.text
                ).strip()
            for hearing_result in item.find_all(
                "div", class_="col-md-7 vs-items-black vs-padding-top-10"
            ):
                result_row["hearing_result"] = hearing_result.text.strip()
            # hearing time
            for hearing_time in item.find_all(
                "div", class_="col-md-2 col-sm-2 col-xs-2 vs-font-18"
            ):
                result_row["hearing_time"] = hearing_time.text.strip()[-5:]
            result_row["case_info"] = re.sub("\s+", " ", case_info).strip()
            result_row["check_date"] = check_date
            result_row["court"] = court.get("title")
            result_row["court_alias"] = court.get("alias")
            result_row["section_name"] = section_name
            result.append(result_row)

    driver.close()
    driver.quit()
    data_frame = convert_data_to_df(
        result, scraper_config.SCRAPER_CONFIG[9]["stage_mapping"]
    )
    return data_frame, court, "success"


def get_links(link_config: dict) -> tuple[DataFrame, dict, str]:
    """extracts linked case"""
    session = WebClient(
        dont_raise_for=[
            404,
        ]
    )
    logger.debug(link_config["case_link"])
    try:
        page = session.get(link_config["case_link"])
    except Exception as e:
        return DataFrame(), link_config, "failure"

    soup = BeautifulSoup(page.content, "html.parser")
    rows = soup.find_all("div", id="vs-items")
    link_court_name = link_case_num = None
    for row in rows:
        cols = row.find_all("div", class_="row vs-item-detail")
        for col in cols:
            if col.find("div", class_="col-md-3") and (
                col.find("div", class_="col-md-3").text.strip() == "Суд 1-ой инстанции:"
            ):
                for first_instance in col.find_all(
                    "div", class_="col-md-7 vs-items-additional-info"
                ):
                    if "Номер дела 1-ой инстанции:" in first_instance.text:
                        link_court_name = (
                            first_instance.contents[0]
                            .text.split("(")[0]
                            .replace("\n", " ")
                        )
                        link_court_name = link_court_name.split("Приговор")[0]
                        link_court_name = link_court_name.split("Решение")[0]
                        link_court_name = link_court_name.split("Определение")[0]
                        link_court_name = re.sub("\s+", " ", link_court_name).strip(
                            ". "
                        )
                        link_case_num = (
                            first_instance.contents[0]
                            .text.split("Номер дела 1-ой инстанции:")[1]
                            .replace("\n", " ")
                        )
                        link_case_num = re.sub("\s+", " ", link_case_num).strip()
                    else:
                        link_case_num = None
                        link_court_name = None
                    break

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
