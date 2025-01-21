import threading
from .webdriver_manager import WebDriverManager
from datetime import datetime
from .get_description import get_description

TIMEOUT_DELAY = 1

class ScraperThread(threading.Thread):
    def __init__(self, url, webdriver_manager:WebDriverManager, callback):
        threading.Thread.__init__(self)
        self.url = url
        self.webdriver_manager = webdriver_manager
        self.callback = callback
        self.daemon = True
        self.start()

    def run(self):
        wifi_safe, description = "", ""
        start_time = datetime.now()
        result = self.webdriver_manager.fetch_page(self.url)
        if result:
            wifi_safe = "Uncertain"
            description, wifi_safe = get_description(self.webdriver_manager.driver)
            end_time = datetime.now()
            duration = end_time - start_time
            print("Scrape successful.", "took", duration.seconds, "seconds.")
        else:
            print(f"Scrape failed: {self.url}")

        self.callback(wifi_safe, description)