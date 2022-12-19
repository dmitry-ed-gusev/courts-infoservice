import random

from selenium import webdriver

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
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

accept_languages = [
    "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "en-US,en;q=0.9",
    "en-US,fr-CA",
]

resolutions = [
    "1280,800",
    "1280,960",
    "1280,1024",
    "1440,900",
    "1440,1080",
    "1600,1200",
    "1920,1080",
    "1920,1200",
]


user_agent = user_agents[random.randrange(0, len(user_agents))]

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--incognito")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--enable-javascript")
firefox_options.add_argument("--enable-automation")
firefox_options.add_argument("--disable-blink-features=AutomationControlled")
firefox_options.add_argument("--user-agent=" + user_agent)
firefox_options.set_preference("http.response.timeout", 60)

gecko_version = "v0.32.0"


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--user-agent=" + user_agent)
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--disable-features=UserAgentClientHint")
chrome_options.add_argument(
    "window-size=" + resolutions[random.randrange(0, len(resolutions))]
)
chrome_prefs = {
    "intl.accept_languages": accept_languages[
        random.randrange(0, len(accept_languages))
    ]
}
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("prefs", chrome_prefs)

chrome_version = "107.0.5304.62"
