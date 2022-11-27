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
                            parser_8,
                            parser_9,
                            )

test_mode = 101
check_date = "13.12.2022"
check_date_dt = datetime.strptime(check_date, "%d.%m.%Y")

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
        court = {"title": "Краснодарский краевой суд (Краснодарский край)", "link": "https://kraevoi--krd.sudrf.ru",
                 "server_num": "1", "alias": "krd-kks",
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
        court = {"title": "Мировой суд (Город Ставрополь)", "link": "https://stavmirsud.ru/officework",
                 "alias": "stav-mir",
                 "check_date": check_date_dt}
        result, out_court, status = parser_7.parse_page(court)
    case 8:
        court = {"title": "arbitr stav", "link": "https://rad.arbitr.ru", "alias": "stav-arbitr",
                 "server_num": "MSK", "check_date": check_date_dt}
        result, out_court, status = parser_8.parse_page(court)
    case 9:
        court = {"title": "vsrf", "link": "https://vsrf.ru", "alias": "vsrf",
                 "check_date": check_date_dt}
        result, out_court, status = parser_9.parse_page(court)
    case 101:
        link_config = {
            "case_link": "https://4kas.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=13197851&case_uid=7fea5f9b-a66a-4d71-8928-7de6bace3677&delo_id=2800001&new=2800001",
            "case_num": "some_case_num",
            "alias": "5kas",
        }
        result, _, status = parser_1.get_links(link_config)
    case 102:
        link_config = {
            "case_link": "https://mos-gorsud.ru/rs/babushkinskij/services/cases/appeal-criminal/details/0159be01-010b-11ed-877a-ff385edec0aa?sessionRangeDateFrom=07.10.2022&sessionRangeDateTo=07.10.2022&formType=fullForm",
            "case_num": "some_case_num",
            "alias": "mosgorsud",
        }
        result, _, status = parser_2.get_links(link_config)
    case 103:
        link_config = {
            "case_link": "https://kraevoi--krd.sudrf.ru/modules.php?name=sud_delo&name_op=case&_uid=d46d6eb3-3723-4ecc-9966-944ddb79671e&_deloId=5&_caseType=0&_new=0&srv_num=1&_hideJudge=0",
            "case_num": "some_case_num",
            "alias": "krd-kks",
        }
        result, _, status = parser_3.get_links(link_config)
    case 104:
        link_config = {"title": "Мировой суд (Город Санкт-Петербург)", "link": "https://mirsud.spb.ru",
                       "alias": "spb-mir",
                       "case_link": "https://mirsud.spb.ru/cases/detail/214/?id=5-906%2F2022-7",
                       "case_num": "some_case_num",
                       }
        result, _, status = parser_4.get_links(link_config)
    case 105:
        link_config = {
            "case_link": "https://mos-sud.ru/354/cases/civil/details/ca2ea371-5bf0-4782-b57c-456dc396274b?sessionRangeDateFrom=03.10.2022&sessionRangeDateTo=03.10.2022&formType=fullForm",
            "case_num": "some_case_num",
            "alias": "mir-msk",
        }
        result, _, status = parser_5.get_links(link_config)
    case 106:
        link_config = {
            "case_link": "https://oblsud--lo.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=11175763&case_uid=315340be-61f9-420e-bce1-96eb76af73d8&result=0&delo_id=5&new=5",
            "case_num": "some_case_num",
            "alias": "lenob-obl",
        }
        result, _, status = parser_6.get_links(link_config)
    case 108:
        link_config = {"case_link": "https://kad.arbitr.ru/card/af9fa8bd-8de7-46cc-83ba-2fe769a056a7",
                       "case_num": "some_case_num",
                       "alias": "arbitr",
                       }
        result, _, status = parser_8.get_links(link_config)
    case 109:
        link_config = {"case_link": "https://vsrf.ru/lk/practice/cases/11582039#11582039",
                       "case_num": "some_case_num",
                       "alias": "vsrf",
                       }
        result, _, status = parser_9.get_links(link_config)
    case _:
        result = []
        status = ""
        out_court = []
# db_tools.load_to_stage(result, db_config)

print(result)
print(len(result))
