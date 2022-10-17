import random
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from courts.utils.utilities import singleton, threadsafe_function
from selenium import webdriver


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
        if not self.__headers or self.__uses > 100:
            self.refresh_cookies()
            self.__uses = 0
        return self.__headers

    @headers.setter
    @threadsafe_function
    def headers(self, value: dict[str, str]):
        self.__headers = value

    def refresh_cookies(self) -> None:
        """opens new page to get cookies for api requests"""
        user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
                       "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
                       "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                       "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) Gecko/20100101 Firefox/105.0",
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77 (Edition Yx 05)",
                       ]

        self.__user_agent = user_agents[random.randrange(0, len(user_agents))]
        resolutions = ["1280,800", "1280,960", "1280,1024", "1440,900", "1440,1080", "1600,1200", "1920,1080",
                       "1920,1200"]
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(
            "--user-agent=" + self.__user_agent)
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-features=UserAgentClientHint")
        chrome_options.add_argument("window-size=" + resolutions[random.randrange(0, len(resolutions))])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        service = ChromeService(ChromeDriverManager().install())
        while True:
            try:
                driver = webdriver.Chrome(service=service, options=chrome_options)
                break
            except:
                time.sleep(3)
        # driver.set_window_position(-2000, 0)
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
            "TE": "trailers"
        }
