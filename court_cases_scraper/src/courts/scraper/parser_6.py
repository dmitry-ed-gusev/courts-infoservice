"""scrap js page of len obl sud"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from loguru import logger

from court_cases_scraper.src.courts.config import scraper_config as config


def parse_page(court: dict) -> tuple[list[dict[str, str]], dict, list[dict[str, str]]]:
    """parses output js page"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    result = []
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--incognito")
    options.add_argument("--window-size=1920,1280")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")
    options.add_argument("--user-agent " + config.USER_AGENT)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = court.get("link") + "/modules.php?name=sud_delo&srv_num=" + court.get("server_num") + "&H_date=" + check_date
    logger.debug(url)
    driver.get(url)
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
    return result, court, config.STAGE_MAPPING_6

