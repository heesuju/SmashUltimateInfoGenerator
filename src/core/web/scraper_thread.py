import threading
from .webdriver_manager import WebDriverManager
from datetime import datetime
from .get_thumbnails import get_thumbnails
from .get_version import get_version
from .get_wifi_safe import get_wifi_safe
from .get_nsfw import get_nsfw
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
        start_time = datetime.now()
        result = self.webdriver_manager.fetch_page(self.url)
        if result:
            img_urls, img_descs = get_thumbnails(self.webdriver_manager.driver)
            version = get_version(self.webdriver_manager.driver)
            wifi_safe = get_wifi_safe(self.webdriver_manager.driver)
            description = get_description(self.webdriver_manager.driver)
            # is_nsfw = get_nsfw(self.webdriver_manager.driver)
            end_time = datetime.now()
            duration = end_time - start_time
            print("Scrape successful.", "took", duration.seconds, "seconds.")
            self.callback(version, img_urls, img_descs, wifi_safe, description)
        else:
            print(f"Scrape failed: {self.url}")