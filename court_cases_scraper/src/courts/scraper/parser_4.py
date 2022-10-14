"""scrap spb miroviye sudy"""
import time
import requests
from loguru import logger
from courts.config import scraper_config as config


def parse_page(court: dict) -> tuple[list[dict[str, str]], dict, list[dict[str, str]]]:
    """parses output page"""
    check_date = court.get("check_date").strftime("%d.%m.%Y")
    session = requests.Session()
    result = []
    case_types = ["adm", "civil", "criminal", "public"]
    for case_type in case_types:
        order_num = 0
        page_num = 1
        while True:
            content_json = None
            while True:
                api_search = court.get("link") + \
                             "/cases/api/search/?adm_person_type=all&article=&civil_person_type=" + \
                             "all&court_number=&criminal_person_type=all&date_from=" + check_date + \
                             "&date_to=" + check_date + "&full_name=&id=&page=" + str(page_num) + "&type=" + case_type
                get_search = session.get(api_search)
                if get_search.status_code == 200:
                    break
                else:
                    time.sleep(2)
            logger.debug(api_search)
            search_id = get_search.json()["id"]
            finished = False
            total_tries = 0
            while not finished:
                total_tries += 1
                content = session.get(court.get("link") + "/cases/api/results/?id=" + search_id)
                if content.status_code == 200:
                    content_json = content.json()
                    finished = content_json["finished"]
                if not finished:
                    time.sleep(2)
                if total_tries > config.MAX_RETRIES:
                    break

            for row in content_json["result"]["data"]:
                order_num += 1
                case_info = None
                if case_type == "adm":
                    section_name = "Дела об АП"
                    if row.get("offenders"):
                        case_info = "Лицо, в отношении которого ведется производство по делу об административном правонарушении: " + \
                                    row.get("offenders") + ". "
                        if row.get("article"):
                            case_info = case_info + "Статья КоАП РФ " + row.get("article") + "."

                elif case_type == "criminal":
                    section_name = "Уголовные дела"
                    if row.get("defendants"):
                        case_info = "Подсудимый: " + row.get("defendants") + ". "
                        if row.get("article"):
                            case_info = case_info + "Статья УК РФ " + row.get("article")
                else:
                    if case_type == "civil":
                        section_name = "Гражданские дела"
                    else:
                        section_name = "Административные дела"
                    case_info = None
                    if row.get("claimants"):
                        case_info = "Истец: " + row.get("claimants") + ". "
                        if row.get("respondents"):
                            case_info = case_info + "Ответчик: " + row.get("respondents") + ". "
                        if row.get("third_parties"):
                            case_info = case_info + "Третьия лица: " + row.get("third_parties") + ". "

                result.append({"case_num": row.get("id"),
                               "case_link": court.get("link") + row.get("url"),
                               "court": court.get("title") + " Участок " + row.get("court_number"),
                               "court_alias": court.get("alias"),
                               "check_date": check_date,
                               "status": row.get("status"),
                               "order_num": order_num,
                               "case_info": case_info,
                               "section_name": section_name
                               })

            if len(content_json["result"]["data"]) == 0:
                break
            else:
                page_num += 1

    return result, court, config.STAGE_MAPPING_4
