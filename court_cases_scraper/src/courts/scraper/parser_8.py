"""scrap arbitr sud"""
from seleniumrequests import Firefox
import json
from loguru import logger
from court_cases_scraper.src.courts.config import scraper_config as config


def parse_json(court: dict, json_data: json) -> list[dict[str, str]]:
    result = []
    for courts in json_data["Result"]["Items"]:
        for one_court in courts["Courts"]:
            for item in one_court["Items"]:
                result_row = {
                    "hearing_time": item.get("Time"),
                    "case_number": item.get("CaseNumber"),
                    "judge": item.get("JudgeName"),
                    "hearing_place": item.get("Place"),
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
                        respondents = " Должники: " + respondent + ", "
                    else:
                        respondents = respondents + respondent + ", "
                if respondents != "":
                    respondents = respondents.rstrip(", ") + ". "

                result_row["case_info"] = plaintiffs + respondents
                result.append(result_row)

    return result

def parse_page(court: dict, cookies: str | None = None) -> tuple[list[dict[str, str]], dict, list[dict[str, str]]]:
    """request json with cookie and parse response"""
    if not cookies:
        raise Exception("No cookie")
    result = []

    check_date = court.get("check_date").strftime("%Y-%m-%d")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
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
        "Cookie": cookies,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }

    data = '{"needConfirm":false,"DateFrom":"' + check_date + 'T00:00:00","Sides":[],"Cases":[],"Judges":[],"JudgesEx":[],"Courts":["' + court.get("server_num") + '"]}'
    logger.debug("Requesting " + court.get("link") + " server " + court.get("server_num") + " date " + check_date)
    req_driver = Firefox()
    url_address = court.get("link") + "/Rad/TimetableDay"
    response = req_driver.request("POST", url_address, data=data, headers=headers)
    if response.status_code != 200:
        raise Exception("request rejected")
    json_data = json.loads(response.content)

    if not json_data["Result"]["needConfirm"]:
        result.extend(parse_json(court, json_data))

    return result, court, config.STAGE_MAPPING_8
