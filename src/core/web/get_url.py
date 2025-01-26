import threading
from .webdriver_manager import WebDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

TIMEOUT_DELAY = 10
GOOGLE_URL = "https://google.com/search?q="
SEARCH_FORMAT = "site:gamebanana.com/mods -site:gamebanana.com/mods/cats -site:gamebanana.com/mods/subscribers -site:gamebanana.com/mods/admin smash ultimate {0}"

class URLFinder(threading.Thread):
    def __init__(
            self, 
            webdriver_manager:WebDriverManager, 
            callback:callable,
            keyword:str
        ):
        threading.Thread.__init__(self)
        self.webdriver_manager = webdriver_manager
        self.callback = callback
        self.keyword = keyword
        self.daemon = True
        self.start()

    def run(self):
        url = GOOGLE_URL + SEARCH_FORMAT.format(self.keyword)
        result = self.webdriver_manager.fetch_page(url)
        links = []
        if result:
            links = get_links(self.webdriver_manager.driver)
            self.callback(links)
        else:
            print(f"Scrape failed: {self.url}")

def get_links(driver)->list[str]:
    try:
        links = []

        wrapper = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search = soup.find_all('div', class_="yuRUbf")
        for h in search:
            links.append(h.a.get('href'))
        return links

    except TimeoutException:
        print("timeout error")