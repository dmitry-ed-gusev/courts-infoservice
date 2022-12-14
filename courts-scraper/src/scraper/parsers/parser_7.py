"""scrap stav mir sud"""
import random
import time

from bs4 import BeautifulSoup
from loguru import logger
from pandas import DataFrame

from scraper.config import scraper_config
from scraper.db.db_tools import convert_data_to_df
from scraper.web.web_client import WebClient


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """parses output page"""
    session = WebClient()
    session.headers = {
        "user-agent": scraper_config.USER_AGENT,
        "cache-control": "private, max-age=0, no-cache",
    }
    check_date = court.get("check_date").strftime("%Y-%m-%d")
    result = []
    case_types = ["caselistus", "caselistcs", "caselistas"]
    for case_type in case_types:
        empty_flag = False
        page_num = 0
        while not empty_flag:
            empty_flag = True
            url = (
                court.get("link")
                + "/"
                + case_type
                + "/?sf5="
                + check_date
                + "&sf5_d="
                + check_date
                + "&pn="
                + str(page_num)
            )
            logger.debug(url)
            time.sleep(random.randrange(2, 4))
            try:
                page = session.get(url)
            except:
                return DataFrame(), court, "failure"
            soup = BeautifulSoup(page.content, "html.parser")
            tables = soup.find_all("table", class_="decision_table")
            # <table class=decision_table>
            for table in tables:
                sections = table.find_all("tr")
                if len(sections) > 2:
                    empty_flag = False
                # tr
                for idx, section in enumerate(sections):
                    # skip header
                    if idx == 0:
                        continue
                    # appending row
                    else:
                        # skip subtables
                        if len(section.find_all("td")) == 2:
                            continue
                        result_row = {}
                        # td
                        for idx_r, row in enumerate(section.find_all("td")):
                            if idx_r == 0:
                                continue
                            if row.text:
                                result_row["col" + str(idx_r)] = row.text.strip()
                            else:
                                result_row["col" + str(idx_r)] = str(
                                    row.contents
                                ).strip()
                            if row.find(href=True):
                                result_row["col" + str(idx_r) + "_link"] = (
                                    court.get("link") + row.find(href=True)["href"]
                                )
                        match case_type:
                            case "caselistcs":
                                result_row["section_name"] = "?????????????????????? ????????"
                                result_row["judge"] = result_row.get("col11")
                                if result_row.get("col4"):
                                    result_row["case_info"] = (
                                        "??????????: " + result_row.get("col4") + ". "
                                    )
                                else:
                                    result_row["case_info"] = ""
                                if result_row.get("col5"):
                                    result_row["case_info"] = (
                                        result_row["case_info"]
                                        + "????????????????: "
                                        + result_row.get("col5")
                                        + ". "
                                    )
                                if result_row.get("col6"):
                                    result_row["case_info"] = (
                                        result_row["case_info"]
                                        + "??????????????????: "
                                        + result_row.get("col6")
                                        + "."
                                    )
                            case "caselistus":
                                result_row["section_name"] = "?????????????????? ????????"
                                result_row["judge"] = result_row.get("col11")
                                if result_row.get("col4"):
                                    result_row["case_info"] = (
                                        "??????????????????????: " + result_row.get("col4") + ". "
                                    )
                                else:
                                    result_row["case_info"] = ""
                                if result_row.get("col5"):
                                    result_row["case_info"] = (
                                        result_row["case_info"]
                                        + "????????????????????: "
                                        + result_row.get("col5")
                                        + ". "
                                    )
                                if result_row.get("col6"):
                                    result_row["case_info"] = (
                                        result_row["case_info"]
                                        + ". ???????????? ????: "
                                        + result_row.get("col6")
                                        + "."
                                    )
                            case "caselistas":
                                result_row[
                                    "section_name"
                                ] = "???????? ???? ???????????????????????????????? ??????????????????????????????"
                                result_row["judge"] = result_row.get("col10")
                                if result_row.get("col4"):
                                    result_row["case_info"] = (
                                        "??????????????????????: " + result_row.get("col4") + ". "
                                    )
                                else:
                                    result_row["case_info"] = ""
                                if result_row.get("col5"):
                                    result_row["case_info"] = (
                                        result_row["case_info"]
                                        + "???????????????????????? ????????: "
                                        + result_row.get("col5")
                                        + ". "
                                    )
                                if result_row.get("col6"):
                                    result_row["case_info"] = (
                                        result_row["case_info"]
                                        + "???????????? ????????: "
                                        + result_row.get("col6")
                                        + "."
                                    )
                        # end match
                        result_row["court"] = (
                            "?????????????? ??????. ???????????????????????????? ????????,  "
                            + result_row.get("col1")
                            + ", ?????????????? "
                            + result_row.get("col2")
                        )
                        result_row["check_date"] = court.get("check_date").strftime(
                            "%d.%m.%Y"
                        )
                        result_row["court_alias"] = court.get("alias")
                        result_row["case_link"] = url
                        # check if row has case number
                        if result_row["col3"] != "[]":
                            result.append(result_row)
                page_num += 1
    data_frame = convert_data_to_df(
        result, scraper_config.SCRAPER_CONFIG[7]["stage_mapping"]
    )
    return data_frame, court, "success"
