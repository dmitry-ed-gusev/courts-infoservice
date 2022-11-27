"""scrap stav mir sud"""
import time
import random
from bs4 import BeautifulSoup
from loguru import logger
from pandas import DataFrame
from courts.web.web_client import WebClient

from courts.config import scraper_config
from courts.db.db_tools import convert_data_to_df


def parse_page(court: dict) -> tuple[DataFrame, dict, str]:
    """parses output page"""
    session = WebClient()
    session.headers = {"user-agent": scraper_config.USER_AGENT,  "cache-control": "private, max-age=0, no-cache"}
    check_date = court.get("check_date").strftime("%Y-%m-%d")
    result = []
    case_types = ["caselistus", "caselistcs", "caselistas"]
    for case_type in case_types:
        empty_flag = False
        page_num = 0
        order_num = 1
        while not empty_flag:
            empty_flag = True
            url = court.get("link") + "/" + case_type + "/?sf5=" + check_date + "&sf5_d=" + check_date + "&pn=" + str(page_num)
            logger.debug(url)
            time.sleep(random.randrange(0, 3))
            try:
                page = session.get(url)
            except:
                return DataFrame(), court, "failure"
            soup = BeautifulSoup(page.content, 'html.parser')
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
                                result_row["col" + str(idx_r)] = str(row.contents).strip()
                            if row.find(href=True):
                                result_row["col" + str(idx_r) + "_link"] = court.get("link") + row.find(href=True)["href"]
                        match case_type:
                            case "caselistcs":
                                result_row["section_name"] = "Гражданские дела"
                                result_row["judge"] = result_row.get("col11")
                                if result_row.get("col4"):
                                    result_row["case_info"] = "Истец: " + result_row.get("col4") + ". "
                                else:
                                    result_row["case_info"] = ""
                                if result_row.get("col5"):
                                    result_row["case_info"] = result_row["case_info"] + "Ответчик: " + result_row.get("col5") + ". "
                                if result_row.get("col6"):
                                    result_row["case_info"] = result_row["case_info"] + "Категория: " + result_row.get("col6") + "."
                            case "caselistus":
                                result_row["section_name"] = "Уголовные дела"
                                result_row["judge"] = result_row.get("col11")
                                if result_row.get("col4"):
                                    result_row["case_info"] = "Потерпевший: " + result_row.get("col4") + ". "
                                else:
                                    result_row["case_info"] = ""
                                if result_row.get("col5"):
                                    result_row["case_info"] = result_row["case_info"] + "Обвиняемый: " + result_row.get("col5") + ". "
                                if result_row.get("col6"):
                                    result_row["case_info"] = result_row["case_info"] + ". Статья УК: " + result_row.get("col6") + "."
                            case "caselistas":
                                result_row["section_name"] = "Дела об административных правонарушениях"
                                result_row["judge"] = result_row.get("col10")
                                if result_row.get("col4"):
                                    result_row["case_info"] = "Потерпевший: " + result_row.get("col4") + ". "
                                else:
                                    result_row["case_info"] = ""
                                if result_row.get("col5"):
                                    result_row["case_info"] = result_row["case_info"] + "Привлекаемое лицо: " + result_row.get("col5") + ". "
                                if result_row.get("col6"):
                                    result_row["case_info"] = result_row["case_info"] + "Статья КоАП: " + result_row.get("col6") + "."
                        # end match
                        result_row["court"] = "Мировой суд. Ставропольский край,  " + result_row.get("col1") + ", участок " + result_row.get(
                            "col2")
                        result_row["check_date"] = court.get("check_date").strftime("%d.%m.%Y")
                        result_row["court_alias"] = court.get("alias")
                        result_row["order_num"] = str(order_num)
                        result_row["case_link"] = url
                        order_num += 1
                        result.append(result_row)
                page_num += 1
    data_frame = convert_data_to_df(result, scraper_config.SCRAPER_CONFIG[7]["stage_mapping"])
    return data_frame, court, "success"
