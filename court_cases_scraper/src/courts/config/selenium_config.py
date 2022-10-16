from fake_useragent import UserAgent
from selenium import webdriver


user_agent = UserAgent()
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--incognito")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--enable-javascript")
firefox_options.add_argument("--enable-automation")
firefox_options.add_argument('--disable-blink-features=AutomationControlled')
firefox_options.add_argument("--user-agent=" + user_agent.random)
