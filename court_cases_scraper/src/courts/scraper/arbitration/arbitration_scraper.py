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

# POST /Rad/TimetableDay HTTP/2
# Host: rad.arbitr.ru
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate, br
# Content-Type: application/json
# X-Requested-With: XMLHttpRequest
# Content-Length: 137
# Origin: https://rad.arbitr.ru
# Connection: keep-alive
# Referer: https://rad.arbitr.ru/
# Cookie: __ddg1_=nWd7rmuxf2kXs53Dc6Vb; ASP.NET_SessionId=g5a5xwk5m2z5qvddwnrpccyd; CUID=f736c4d4-0577-456a-a638-241cc35a6c0a:7hIjj/Q7UDGHv6GWM1LSVA==; _ga=GA1.2.1555853159.1665704820; _gid=GA1.2.888777824.1665704820; _ym_uid=1665704822266963732; _ym_d=1665704822; tmr_reqNum=9; tmr_lvid=9eab191bf43e7fba9e8e5eff81520872; tmr_lvidTS=1665704821907; _ym_isad=2; tmr_detect=0%7C1665706347965; pr_fp=ccd700beaa19eafa8a48c0f6da8b33e7752b2ae8a5ec2d091ee2286fd7475e61; rcid=bceef606-c664-4d18-9cd0-c7a73fd9afc0; wasm=c22f64d8fe6d8e5b84ee80840b3c892f

# curl 'https://rad.arbitr.ru/Rad/TimetableDay' -X POST -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:105.0) Gecko/20100101 Firefox/105.0' -H 'Accept: application/json, text/javascript, */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/json' -H 'X-Requested-With: XMLHttpRequest' -H 'x-date-format: iso' -H 'Origin: https://rad.arbitr.ru' -H 'Connection: keep-alive' -H 'Referer: https://rad.arbitr.ru/' -H 'Cookie: __ddg1_=nWd7rmuxf2kXs53Dc6Vb; ASP.NET_SessionId=g5a5xwk5m2z5qvddwnrpccyd; CUID=f736c4d4-0577-456a-a638-241cc35a6c0a:7hIjj/Q7UDGHv6GWM1LSVA==; _ga=GA1.2.1555853159.1665704820; _gid=GA1.2.888777824.1665704820; _ym_uid=1665704822266963732; _ym_d=1665704822; tmr_reqNum=9; tmr_lvid=9eab191bf43e7fba9e8e5eff81520872; tmr_lvidTS=1665704821907; _ym_isad=2; tmr_detect=0%7C1665706347965; pr_fp=ccd700beaa19eafa8a48c0f6da8b33e7752b2ae8a5ec2d091ee2286fd7475e61; rcid=bceef606-c664-4d18-9cd0-c7a73fd9afc0; wasm=c22f64d8fe6d8e5b84ee80840b3c892f' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' --data-raw '{"needConfirm":false,"mode":"table","DateFrom":"2022-10-17T00:00:00","Sides":[],"Cases":[],"Judges":[],"JudgesEx":[],"Courts":["FASVVO"]}'

cookie_str = '__ddg1_=nWd7rmuxf2kXs53Dc6Vb; ASP.NET_SessionId=g5a5xwk5m2z5qvddwnrpccyd; CUID=f736c4d4-0577-456a-a638-241cc35a6c0a:7hIjj/Q7UDGHv6GWM1LSVA==; _ga=GA1.2.1555853159.1665704820; _gid=GA1.2.888777824.1665704820; _ym_uid=1665704822266963732; _ym_d=1665704822; tmr_reqNum=15; tmr_lvid=9eab191bf43e7fba9e8e5eff81520872; tmr_lvidTS=1665704821907; _ym_isad=2; tmr_detect=0%7C1665708138966; pr_fp=ccd700beaa19eafa8a48c0f6da8b33e7752b2ae8a5ec2d091ee2286fd7475e61; rcid=d9187501-bc4d-495d-96dd-3154eeeae743; wasm=9aa81828dc6c312097d5cc53e1ef8adb'
cookie_dict = {
    "__ddg1_": "nWd7rmuxf2kXs53Dc6Vb",
    "ASP.NET_SessionId": "g5a5xwk5m2z5qvddwnrpccyd",
    "CUID": "f736c4d4-0577-456a-a638-241cc35a6c0a:7hIjj/Q7UDGHv6GWM1LSVA==",
    "_ga": "GA1.2.1555853159.1665704820",
    "_gid": "GA1.2.888777824.1665704820",
    "_ym_uid": "1665704822266963732",
    "_ym_d": "1665704822",
    "tmr_reqNum": "13",
    "tmr_lvid": "9eab191bf43e7fba9e8e5eff81520872",
    "tmr_lvidTS": "1665704821907",
    "_ym_isad": "2",
    "tmr_detect": "0%7C1665708138966",
    "pr_fp": "ccd700beaa19eafa8a48c0f6da8b33e7752b2ae8a5ec2d091ee2286fd7475e61",
    "_gat": "1",
    "_gat_FrontEndTracker": "1",
    "_dc_gtm_UA-157906562-1": "1",
    "wasm": "9a28685a4082f18c23ae0cfd4911e4aa",
    "rcid": "d9187501-bc4d-495d-96dd-3154eeeae743"
}

# POST /Rad/TimetableDay HTTP/2
# Host: rad.arbitr.ru
# User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:105.0) Gecko/20100101 Firefox/105.0
# Accept: application/json, text/javascript, */*
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate, br
# Content-Type: application/json
# X-Requested-With: XMLHttpRequest
# x-date-format: iso
# Content-Length: 122
# Origin: https://rad.arbitr.ru
# Connection: keep-alive
# Referer: https://rad.arbitr.ru/
# Cookie: __ddg1_=nWd7rmuxf2kXs53Dc6Vb; ASP.NET_SessionId=g5a5xwk5m2z5qvddwnrpccyd; CUID=f736c4d4-0577-456a-a638-241cc35a6c0a:7hIjj/Q7UDGHv6GWM1LSVA==; _ga=GA1.2.1555853159.1665704820; _gid=GA1.2.888777824.1665704820; _ym_uid=1665704822266963732; _ym_d=1665704822; tmr_reqNum=15; tmr_lvid=9eab191bf43e7fba9e8e5eff81520872; tmr_lvidTS=1665704821907; _ym_isad=2; tmr_detect=0%7C1665708138966; pr_fp=ccd700beaa19eafa8a48c0f6da8b33e7752b2ae8a5ec2d091ee2286fd7475e61; rcid=d9187501-bc4d-495d-96dd-3154eeeae743; wasm=9aa81828dc6c312097d5cc53e1ef8adb
# Sec-Fetch-Dest: empty
# Sec-Fetch-Mode: cors
# Sec-Fetch-Site: same-origin
# TE: trailers

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "application/json, text/javascript, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Content-Length": "102",
    "X-Requested-With": "XMLHttpRequest",
    "x-date-format": "iso",
    "Host": "rad.arbitr.ru",
    "Origin": "https://rad.arbitr.ru",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://rad.arbitr.ru/",
    "Cookie": cookie_str,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}
payload1 = {"needConfirm": False,"DateFrom":"2022-10-03T00:00:00","Sides":[],"Cases":[],"Judges": [],"JudgesEx":[],"Courts":["FASZSO"]}

payload2 = {
    "DateFrom": "2022-10-01T00:00:00",
    "Sides": [],
    "Cases": [],
    "Judges": [],
    "JudgesEx": [],
    "Courts": ["FASVVO"]
}

webclient = WebClient(headers=headers)
response = webclient.post("https://rad.arbitr.ru/Rad/TimetableDay", data=payload1)

print(response.cookies)
print(response.status_code)
