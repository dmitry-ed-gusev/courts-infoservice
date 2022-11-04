"""
script for debugging
don't include in setup
"""
from datetime import datetime
import os
from dotenv import load_dotenv
from loguru import logger
from courts.db import db_tools
from courts.scraper import (parser_1,
                            parser_2,
                            parser_3,
                            parser_4,
                            parser_5,
                            parser_6,
                            parser_7,
                            parser_8)

test_mode = 108
check_date = "10.10.2022"
check_date_dt = datetime.strptime("10.10.2022", "%d.%m.%Y")

# Load environment variables from .env file from the project root dir
load_dotenv()
db_config = {"host": os.environ["MYSQL_HOST"],
             "port": os.environ["MYSQL_PORT"],
             "user": os.environ["MYSQL_USER"],
             "passwd": os.environ["MYSQL_PASS"],
             "db": os.environ["MYSQL_DB"]}

match test_mode:
    case 1:
        court = {"title": "Василеостровский районный суд", "link": "https://vos--spb.sudrf.ru", "server_num": "1",
                 "alias": "spb-vos",
                 "check_date": check_date_dt}
        result, out_court, status = parser_1.parse_page(court)
    case 3:
        court = {"title": "Краснодарский краевой суд (Краснодарский край)", "link": "https://kraevoi--krd.sudrf.ru", "server_num": "1", "alias": "krd-kks",
                 "check_date": check_date_dt}
        result, out_court, status = parser_3.parse_page(court)
    case 4:
        court = {"title": "Мировой суд (Город Санкт-Петербург)", "link": "https://mirsud.spb.ru", "alias": "spb-mir",
                 "check_date": check_date_dt}
        result, out_court, status = parser_4.parse_page(court)
    case 5:
        court = {"title": "Мировой суд (Город Москва)", "link": "https://mos-sud.ru", "alias": "msk-mir",
                 "check_date": check_date_dt}
        result, out_court, status = parser_5.parse_page(court)
    case 7:
        court = {"title": "Мировой суд (Город Ставрополь)", "link": "https://stavmirsud.ru/officework", "alias": "stav-mir",
                 "check_date": check_date_dt}
        result, out_court, status = parser_7.parse_page(court)
    case 8:
        court = {"title": "arbitr stav", "link": "https://rad.arbitr.ru", "alias": "stav-arbitr",
                 "server_num": "MSK", "check_date": check_date_dt}
        result, out_court, status = parser_8.parse_page(court)
    case 101:
        link_config = {"case_link": "http://5kas.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=1101651&case_uid=f60da665-e23c-4f1a-81bf-bd02a3b0ea9b&delo_id=2450001&new=2450001"}
        result, status = parser_1.get_links(link_config)
    case 102:
        link_config = {"case_link": "https://mos-gorsud.ru/rs/babushkinskij/services/cases/kas/details/fff4b211-3f0b-11ed-8a4d-41cc963c94b4?sessionRangeDateFrom=09.09.2022&sessionRangeDateTo=09.09.2022&formType=fullForm"}
        result, status = parser_2.get_links(link_config)
    case 103:
        link_config = {"case_link": "https://kraevoi--krd.sudrf.ru/modules.php?name=sud_delo&name_op=case&_uid=d46d6eb3-3723-4ecc-9966-944ddb79671e&_deloId=5&_caseType=0&_new=0&srv_num=1&_hideJudge=0"}
        result, status = parser_3.get_links(link_config)
    case 104:
        link_config = {"title": "Мировой суд (Город Санкт-Петербург)", "link": "https://mirsud.spb.ru", "alias": "spb-mir",
                 "case_link": "https://mirsud.spb.ru/cases/detail/214/?id=5-906%2F2022-7"}
        result, status = parser_4.get_links(link_config)
    case 105:
        link_config = {"case_link": "https://mos-sud.ru/137/cases/civil/details/bf9b2703-98d0-4a4b-baad-8acb0821e220?sessionRangeDateFrom=03.10.2022&sessionRangeDateTo=03.10.2022&formType=fullForm"}
        result, status = parser_5.get_links(link_config)
    case 106:
        link_config = {"case_link": "https://oblsud--lo.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=11175763&case_uid=315340be-61f9-420e-bce1-96eb76af73d8&result=0&delo_id=5&new=5"}
        result, status = parser_6.get_links(link_config)
    case 108:
        link_config = {"case_link": "https://kad.arbitr.ru/card/4dd47f2c-8d43-47d2-aa4e-2da1682ca58c"}
        result, status = parser_8.get_links(link_config)
    case _:
        result = []
        status = ""
        out_court = []
# db_tools.load_to_stage(result, db_config)

print(result)
print(len(result))
