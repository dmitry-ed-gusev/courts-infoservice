import os
from seleniumrequests import Firefox
import json
from selenium import webdriver
from fake_useragent import UserAgent
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
import webbrowser
import subprocess

from court_cases_scraper.src.courts.config import scraper_config as config

base_url = "https://rad.arbitr.ru"


user_agent = UserAgent()
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--incognito")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--enable-webgl")
firefox_options.add_argument("--enable-javascript")
firefox_options.add_argument("--dns-prefetch-disable")
firefox_options.add_argument("--dom-max_script_run_time=15")
firefox_options.add_argument("--enable-automation")
firefox_options.add_argument('--disable-blink-features=AutomationControlled')
firefox_options.add_argument("--user-agent=" + user_agent.random)
firefox_service = Service(GeckoDriverManager().install())

driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
driver.get(base_url)

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# Change chrome driver path accordingly
# chrome_service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
# driver.get(base_url)
# print(driver.title)

cookies = ""
for cookie in driver.get_cookies():
    cookies = cookies + "; " + cookie["name"] + "=" +cookie["value"]
cookies = cookies.lstrip("; ")
driver.close()

print(cookies)
req_driver = Firefox()

url_wasm1 = base_url + "/Wasm/api/v1/wasm.js?_=1665703111456"
headers_wasm1 = {"Accept": "text/javascript, application/javascript, */*",
                 "Accept-Language": "en-US,en;q=0.5",
                 "Accept-Encoding": "gzip, deflate, br",
                 "X-Requested-With": "XMLHttpRequest",
                 "Connection": "keep-alive",
                 "Referer": "https://rad.arbitr.ru/",
                 "Cookie": cookies,
                 "Sec-Fetch-Dest": "empty",
                 "Sec-Fetch-Mode": "cors",
                 "Sec-Fetch-Site": "same-origin",
                 "Sec-GPC": "1",
                 "TE": "trailers",
}

response = req_driver.request("GET", url_wasm1, headers=headers_wasm1)
wasm_script = response.content
print(wasm_script)

url_address = base_url + "/Rad/TimetableDay"
check_date = "2022-10-03"
court = "STAVROPOL"
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
    # "Cookie": "__ddg1_=kf9NgkEerjpCgTalTIJk; CUID=3e580b74-d0bd-45a1-b862-47c4b8d5a285:DFAVDDhROvs/vvWjyM0gJw==; _ga=GA1.2.1872885167.1665652603; _gid=GA1.2.39510830.1665652603; tmr_lvid=f078ec6df95b53b35d1fc8c99bfdf399; tmr_lvidTS=1665652603637; _ym_uid=1665652604972701208; _ym_d=1665652604; _ym_isad=2; ASP.NET_SessionId=i55c02ifrbjsynybplmots2h; _gat=1; _gat_FrontEndTracker=1; _dc_gtm_UA-157906562-1=1; pr_fp=e3c17fcd3b911c532c183a1d14a139240a6cc4b820ff38d1f3d78366f94b297c; wasm=2ab22cb317e3a9973bb1b1d046a8b9b8; tmr_detect=0%7C1665669427162; tmr_reqNum=28",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}

data = '{"needConfirm":false,"DateFrom":"' + check_date + 'T00:00:00","Sides":[],"Cases":[],"Judges":[],"JudgesEx":[],"Courts":["' + court + '"]}'





response = req_driver.request("POST", url_address, data=data, headers=headers)
json_data = json.loads(response.content)
req_driver.close()
print(len(json_data))
print(json_data)
