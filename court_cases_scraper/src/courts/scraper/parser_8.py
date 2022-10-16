"""scrap arbitr sud"""
import time
import random
from seleniumrequests import Firefox
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
import json
from loguru import logger

from pandas import DataFrame

from courts.config import scraper_config as config
from courts.db.db_tools import convert_data_to_df


def refresh_cookies(base_url: str) -> tuple[str, str]:
    """opens new page to get cookies for api requests"""
    user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
                   "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
                   "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                   "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                   ]

    user_agent = user_agents[random.randrange(0, len(user_agents))]
    resolutions = ["1280,800", "1280,960", "1280,1024", "1440,900", "1440,1080", "1600,1200", "1920,1080", "1920,1200"]
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(
        "--user-agent=" + user_agent)
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--disable-features=UserAgentClientHint")
    chrome_options.add_argument("window-size=" + resolutions[random.randrange(0, len(resolutions))])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    service = ChromeService(ChromeDriverManager().install())
    while True:
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            break
        except:
            time.sleep(3)
    # driver.set_window_position(-2000, 0)
    driver.get(base_url)
    # waiting for scripts to complete and generate last cookie - wasm
    while "wasm" not in (i["name"] for i in driver.get_cookies()):
        time.sleep(3)

    cookies = ""
    for cookie in driver.get_cookies():
        cookies = cookies + "; " + cookie["name"] + "=" + cookie["value"]
    cookies = cookies.lstrip("; ")
    driver.close()
    return cookies, user_agent


def parse_arbitr_json(court: dict, json_data: json) -> list[dict[str, str]]:
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
    conf = config.CookiesArbitrary()
    if len(conf.cookies) == 0:
        conf.cookies, conf.user_agent = refresh_cookies(court.get("link"))

    result = []

    check_date = court.get("check_date").strftime("%Y-%m-%d")
    headers = {
        "User-Agent": conf.user_agent,
        "Accept": "application/json, text/javascript, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "x-date-format": "iso",
        "Origin": "https://rad.arbitr.ru",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://rad.arbitr.ru/",
        "Cookie": conf.cookies,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }

    data = '{"needConfirm":false,"DateFrom":"' + check_date + 'T00:00:00","Sides":[],"Cases":[],"Judges":[],"JudgesEx":[],"Courts":["' + court.get(
        "server_num") + '"]}'
    logger.debug("Requesting " + court.get("link") + " server " + court.get("server_num") + " date " + check_date)
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    while True:
        try:
            req_driver = Firefox(options=options)
            break
        except:
            time.sleep(3)
    url_address = court.get("link") + "/Rad/TimetableDay"
    retries = 0
    status_code = 0
    while True:
        retries += 1
        if retries > 4:
            return DataFrame(), court, "failure"
        try:
            response = req_driver.request("POST", url_address, data=data, headers=headers)
            status_code = response.status_code
        except Exception as e:
            time.sleep(random.randrange(0, 3))
            status_code = -1
        if status_code == 200:
            break
        if status_code in (429, 403):
            conf.cookies = refresh_cookies(court.get("link"))

    json_data = json.loads(response.content)

    if not json_data["Result"]["needConfirm"]:
        result.extend(parse_arbitr_json(court, json_data))
    else:
        for i in range(0, 10):
            time.sleep(random.randrange(2, 5))
            data = '{"needConfirm":false,"DateFrom":"' + check_date + 'T00:00:00","Sides":[],"Cases":["' + str(
                i) + '/20"],"Judges":[],"JudgesEx":[],"Courts":["' + court.get(
                "server_num") + '"]}'
            status_code = 0
            retries = 0
            while True:
                retries += 1
                if retries > 4:
                    return DataFrame(), court, "failure"
                try:
                    response = req_driver.request("POST", url_address, data=data, headers=headers)
                    status_code = response.status_code
                except Exception as e:
                    time.sleep(random.randrange(2, 5))
                    status_code = -1
                if status_code == 200:
                    break
                if status_code in (429, 403):
                    conf.cookies = refresh_cookies(court.get("link"))

            json_data = json.loads(response.content)
            result.extend(parse_arbitr_json(court, json_data))

    req_driver.close()
    data_frame = convert_data_to_df(result, config.STAGE_MAPPING_8)
    return data_frame, court, "success"
