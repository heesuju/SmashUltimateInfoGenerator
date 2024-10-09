from web.webdriver_singleton import WebDriverSingleton
import threading

class WebDriverManager:
    def __init__(self):
        self.driver = WebDriverSingleton.get_instance()
        self.lock = threading.Lock()

    def fetch_page(self, url):
        with self.lock:
            try:
                self.driver.get(url)
                # page_source = self.driver.execute_script("return document.body.outerHTML;")
                return True
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                return None