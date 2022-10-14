#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Temporary scraper/parser for arbitration courts.
"""

import logging
import logging.config
from courts.web.web_client import WebClient
from courts.config.logger_config import LOGGING_CONFIG

log = logging.getLogger(__name__)

logging.config.dictConfig(LOGGING_CONFIG)
log.info("Starting...")

webclient = WebClient()

# response1 = webclient.get("https://rad.arbitr.ru/")
# print(response1.cookies)

payload = """{
    "needConfirm": False,
    "DateFrom": "2022-10-03T00:00:00",
    "Sides": [],
    "Cases": [],
    "Judges": [],
    "JudgesEx": [],
    "Courts": ["FASZSO"]
}"""

response2 = webclient.get("https://rad.arbitr.ru/Rad/TimetableMonth", params={"request": payload})
print(response2.cookies)
