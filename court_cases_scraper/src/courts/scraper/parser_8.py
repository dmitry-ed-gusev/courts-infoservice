"""scrap arbitr sud"""
import time
import random
from seleniumrequests import Firefox
from selenium import webdriver
import json
from loguru import logger

from pandas import DataFrame

from courts.config import scraper_config as config
from courts.db.db_tools import convert_data_to_df
from courts.common.cookiesArbitrary import CookiesArbitrary


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
            response = req_driver.request("POST", url_address, data=data, headers=conf.headers)
            status_code = response.status_code
        except Exception as e:
            time.sleep(random.randrange(0, 3))
            status_code = -1
        if status_code == 200:
            break
        if status_code in (429, 403):
            conf.refresh_cookies()

    json_data = json.loads(response.content)

    if not json_data["Result"]["needConfirm"]:
        result.extend(parse_arbitrary_json(court, json_data))
    else:
        for i in range(0, 10):
            logger.debug("Requesting " + court["alias"] + " for " + check_date + " part " + str(i + 1) + " of 10.")
            time.sleep(random.randrange(2, 5))
            data = '{"needConfirm":false,"DateFrom":"' + check_date + 'T00:00:00","Sides":[],"Cases":["' + str(
                i) + '/20"],"Judges":[],"JudgesEx":[],"Courts":["' + court.get(
                "server_num") + '"]}'
            retries = 0
            while True:
                retries += 1
                if retries > 4:
                    return DataFrame(), court, "failure"
                try:
                    response = req_driver.request("POST", url_address, data=data, headers=conf.headers)
                    status_code = response.status_code
                except Exception as e:
                    time.sleep(random.randrange(2, 5))
                    status_code = -1
                if status_code == 200:
                    break
                if status_code in (429, 403):
                    conf.refresh_cookies()

            json_data = json.loads(response.content)
            result.extend(parse_arbitrary_json(court, json_data))

    req_driver.close()
    data_frame = convert_data_to_df(result, config.STAGE_MAPPING_8)
    return data_frame, court, "success"
