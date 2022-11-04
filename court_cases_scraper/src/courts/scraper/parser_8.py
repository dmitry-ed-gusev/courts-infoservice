"""scrap arbitr sud"""
import time
import random
import json
from bs4 import BeautifulSoup
from loguru import logger
from pandas import DataFrame
from selenium import webdriver
from seleniumrequests import Firefox
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from courts.config import scraper_config
from courts.db.db_tools import convert_data_to_df
from courts.common.cookiesArbitrary import CookiesArbitrary
from courts.config import selenium_config


def parse_arbitrary_json(court: dict, json_data: json) -> list[dict[str, str]]:
    result = []
    for courts in json_data["Result"]["Items"]:
        for one_court in courts["Courts"]:
            for item in one_court["Items"]:
                result_row = {
                    "hearing_time": item.get("Time"),
                    "case_num": item.get("CaseNumber"),
                    "judge": item.get("JudgeName"),
                    "hearing_place": item.get("Place"),
                    "stage": item.get("SessionStateString"),
                    "case_link": "https://kad.arbitr.ru/card/" + item.get("CaseId"),
                    "court": court.get("title"),
                    "court_alias": court.get("alias"),
                    "check_date": court.get("check_date").strftime("%d.%m.%Y"),
                }

                plaintiffs = ""
                for idx, plaintiff in enumerate(item["Plaintiffs"]):
                    if idx == 0:
                        plaintiffs = "Кредиторы (заявители): " + plaintiff + ", "
                    else:
                        plaintiffs = plaintiffs + plaintiff + ", "
                if plaintiffs != "":
                    plaintiffs = plaintiffs.rstrip(", ") + ". "

                respondents = ""
                for idx, respondent in enumerate(item["Respondents"]):
                    if idx == 0:
                        respondents = "Должники: " + respondent + ", "
                    else:
                        respondents = respondents + respondent + ", "
                if respondents != "":
                    respondents = respondents.rstrip(", ") + ". "

                result_row["case_info"] = (plaintiffs + respondents).strip(" ")
                result.append(result_row)
        for item in courts["Items"]:
            result_row = {
                "hearing_time": item.get("Time"),
                "case_num": item.get("CaseNumber"),
                "judge": item.get("JudgeName"),
                "hearing_place": item.get("Place"),
                "stage": item.get("SessionStateString"),
                "case_link": "https://kad.arbitr.ru/card/" + item.get("CaseId"),
                "court": court.get("title"),
                "court_alias": court.get("alias"),
                "check_date": court.get("check_date").strftime("%d.%m.%Y"),
            }

            plaintiffs = ""
            for idx, plaintiff in enumerate(item["Plaintiffs"]):
                if idx == 0:
                    plaintiffs = "Кредиторы (заявители): " + plaintiff + ", "
                else:
                    plaintiffs = plaintiffs + plaintiff + ", "
            if plaintiffs != "":
                plaintiffs = plaintiffs.rstrip(", ") + ". "

            respondents = ""
            for idx, respondent in enumerate(item["Respondents"]):
                if idx == 0:
                    respondents = "Должники: " + respondent + ", "
                else:
                    respondents = respondents + respondent + ", "
            if respondents != "":
                respondents = respondents.rstrip(", ") + ". "

            result_row["case_info"] = (plaintiffs + respondents).strip(" ")
            result.append(result_row)

    return result


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """request json with cookie and parse response"""
    conf = CookiesArbitrary()

    result = []
    check_date = court.get("check_date").strftime("%Y-%m-%d")
    data = '{"needConfirm":false,"DateFrom":"' + check_date + 'T00:00:00","Sides":[],"Cases":[],"Judges":[],"JudgesEx":[],"Courts":["' + court.get(
        "server_num") + '"]}'
    logger.debug("Requesting " + court.get("link") + " server " + court.get("server_num") + " date " + check_date)
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    retries = 0
    while True:
        retries += 1
        if retries > 4:
            return DataFrame(), court, "failure"
        try:
            req_driver = Firefox(options=options)
            break
        except:
            time.sleep(3)
    url_address = court.get("link") + "/Rad/TimetableDay"
    retries = 0
    while True:
        retries += 1
        if retries > 4:
            return DataFrame(), court, "failure"
        try:
            response = req_driver.request("POST", url_address, data=data, headers=conf.headers)
            status_code = response.status_code
            json_data = json.loads(response.content)
        except Exception as e:
            time.sleep(random.randrange(0, 3))
            status_code = -1
        if status_code == 200:
            break
        if status_code in (429, 403):
            conf.refresh_cookies()

    if not json_data["Result"]["needConfirm"]:
        result.extend(parse_arbitrary_json(court, json_data))
    else:
        for i in range(0, 10):
            logger.debug("Requesting " + court["alias"] + " for " + check_date + " part " + str(i + 1) + " of 10.")
            time.sleep(random.randrange(3, 5))
            data = '{"needConfirm":false,"DateFrom":"' + check_date + 'T00:00:00","Sides":[],"Cases":["' + str(
                i) + '/20"],"Judges":[],"JudgesEx":[],"Courts":["' + court.get(
                "server_num") + '"]}'
            retries = 0
            while True:
                retries += 1
                if retries > 4:
                    req_driver.close()
                    return DataFrame(), court, "failure"
                try:
                    response = req_driver.request("POST", url_address, data=data, headers=conf.headers)
                    status_code = response.status_code
                    json_data = json.loads(response.content)
                except Exception as e:
                    time.sleep(random.randrange(3, 5))
                    status_code = -1
                if status_code == 200:
                    break
                if status_code in (429, 403):
                    conf.refresh_cookies()

            result.extend(parse_arbitrary_json(court, json_data))
    data_frame = convert_data_to_df(result, scraper_config.SCRAPER_CONFIG[8]["stage_mapping"])
    retries = 0
    while True:
        retries += 1
        if retries > 4:
            break
        try:
            req_driver.close()
            break
        except:
            time.sleep(3)
    return data_frame, court, "success"


def get_links(link_config: dict) -> tuple[DataFrame, str]:
    """extracts linked cases and case_uid"""
    user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
                   "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
                   "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                   "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) Gecko/20100101 Firefox/105.0",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                   ]

    user_agent = user_agents[random.randrange(0, len(user_agents))]

    accept_languages = ["ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                        "en-US,en;q=0.9",
                        "en-US,fr-CA",
                        ]
    accept_language = accept_languages[random.randrange(0, len(accept_languages))]

    resolutions = ["1280,800", "1280,960", "1280,1024", "1440,900", "1440,1080", "1600,1200", "1920,1080",
                   "1920,1200"]

    resolution = resolutions[random.randrange(0, len(resolutions))]

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--user-agent=" + user_agent)
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--disable-features=UserAgentClientHint")
    chrome_options.add_argument("window-size=" + resolution)
    chrome_prefs = {"intl.accept_languages": accept_language}
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    chrome_service = ChromeService(ChromeDriverManager().install())
    while True:
        try:
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
            driver.minimize_window()
            break
        except Exception as ce:
            time.sleep(3)
    logger.debug(link_config["case_link"])
    retries = 0
    while True:
        time.sleep(random.randrange(0, 3))
        retries += 1
        if retries > 4:
            driver.close()
            return DataFrame(), "failure"
        try:
            driver.get(link_config["case_link"])
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            break
        except:
            None

    # waiting for scripts to complete and generate last cookie - wasm

    while len(soup.find_all("div", id="b-case-header")) == 0:
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    result = []
    rows = soup.find_all("div", id="b-case-header")
    for row in rows:
        cols = row.find_all("span", class_="js-case-header-case_num", attrs={"data-instance_level": "1"})
        for col in cols:
            data_row = {"case_link": link_config["case_link"],
                        "case_num": [link_config["case_num"], ],
                        "link_case_num": col.text.strip(),
                        "is_primary": True,
                        "link_level": "1",
                        }
            result.append(data_row)

        cols = row.find_all("span", class_="js-case-header-case_num", attrs={"data-instance_level": "2"})
        for col in cols:
            data_row = {"case_link": link_config["case_link"],
                        "case_num": [link_config["case_num"], ],
                        "link_case_num": col.text.strip(),
                        "is_primary": True,
                        "link_level": "2",
                        }
            result.append(data_row)

        cols = row.find_all("span", class_="js-case-header-case_num", attrs={"data-instance_level": "3"})
        for col in cols:
            data_row = {"case_link": link_config["case_link"],
                        "case_num": [link_config["case_num"], ],
                        "link_case_num": col.text.strip(),
                        "is_primary": True,
                        "link_level": "3",
                        }
            result.append(data_row)

        cols = row.find_all("span", class_="js-case-header-case_num", attrs={"data-instance_level": "4,2"})
        for col in cols:
            data_row = {"case_link": link_config["case_link"],
                        "case_num": [link_config["case_num"], ],
                        "link_case_num": col.text.strip(),
                        "is_primary": True,
                        "link_level": "4",
                        }
            result.append(data_row)

        cols = row.find_all("span", class_="js-instance_numbers-rolloverHtml")
        for col in cols:
            linked_numbers = col.get_text(strip=True, separator='<br>').split("<br>")
            for linked_number in linked_numbers:
                for linked_number_1 in linked_number.split(","):
                    data_row = {"case_link": link_config["case_link"],
                                "case_num": [link_config["case_num"], ],
                                "link_case_num": linked_number_1.strip(),
                                }
                    result.append(data_row)

    result_df = DataFrame(result)
    return result_df, "success"
