"""scrap moscow mir courts"""
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import re
import random
from bs4 import BeautifulSoup
from loguru import logger
from courts.config import scraper_config as config


def parse_page(court: dict) -> tuple[list[dict[str, str]], dict, list[dict[str, str]]]:
    """parses mos sud page with paging"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    user_agent = UserAgent()
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--incognito")
    options.add_argument(
        "--window-size=" + str(1920 + random.randrange(-200, 200)) + "," + str(1024 + random.randrange(-200, 200)))
    options.add_argument("--disable-gpu")
    options.add_argument("--nogpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--user-agent " + user_agent.random)
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    result = []
    page_num = 1
    pages_total = 1
    order_num = 0
    while True:
        url = court.get(
            "link") + "/hearing?hearingRangeDateFrom=" + check_date + "&hearingRangeDateTo=" + check_date + "&page=" + str(
            page_num)
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
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
    driver.close()
    return result, court, config.STAGE_MAPPING_5

