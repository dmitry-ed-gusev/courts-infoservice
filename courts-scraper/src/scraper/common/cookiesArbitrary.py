import time

from scraper.config import selenium_config as reloaded_selenium_config
from scraper.utils.utilities import singleton, threadsafe_function
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@singleton
class CookiesArbitrary:
    """class to work with arbitrary cookies"""

    def __init__(self):
        self.__headers: dict[str, str] = {}
        self.__base_url: str = "https://rad.arbitr.ru"
        self.__cookies: str | None = None
        self.__user_agent: str | None = None
        self.__uses: int = 0

    @property
    @threadsafe_function
    def cookies(self) -> str:
        self.__uses += 1
        if not self.__cookies or self.__uses > 100:
            self.refresh_cookies()
            self.__uses = 0
        return self.__cookies

    @cookies.setter
    @threadsafe_function
    def cookies(self, value: str):
        self.__cookies = value

    @property
    @threadsafe_function
    def user_agent(self) -> str:
        return self.__user_agent

    @user_agent.setter
    @threadsafe_function
    def user_agent(self, value: str):
        self.__user_agent = value

    @property
    @threadsafe_function
    def headers(self) -> dict[str, str]:
        self.__uses += 1
        if not self.__headers or self.__uses > 50:
            self.refresh_cookies()
            self.__uses = 0
        return self.__headers

    @headers.setter
    @threadsafe_function
    def headers(self, value: dict[str, str]):
        self.__headers = value

    def refresh_cookies(self) -> None:
        """opens new page to get cookies for api requests"""

        self.__user_agent = reloaded_selenium_config.user_agent

        chrome_service = ChromeService(
            ChromeDriverManager(
                version=reloaded_selenium_config.chrome_version
            ).install()
        )
        while True:
            try:
                driver = webdriver.Chrome(
                    service=chrome_service,
                    options=reloaded_selenium_config.chrome_options,
                )
                break
            except Exception as ce:
                time.sleep(3)

        driver.minimize_window()
        driver.get(self.__base_url)
        # waiting for scripts to complete and generate last cookie - wasm
        while "wasm" not in (i["name"] for i in driver.get_cookies()):
            time.sleep(3)

        cookies = ""
        for cookie in driver.get_cookies():
            cookies = cookies + "; " + cookie["name"] + "=" + cookie["value"]
        cookies = cookies.lstrip("; ")
        driver.close()
        self.__cookies = cookies
        self.__uses = 0
        self.__headers = {
            "User-Agent": self.__user_agent,
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
            "Cookie": self.__cookies,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }
