from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import defs
from threading import Thread

class Selenium(Thread):
    def __init__(self, url:str, callback):
        super().__init__()
        self.url = url
        self.callback = callback
        self.version = defs.DEFAULT_VERSION
        self.img_url = ""

    def get_elements(self, driver):
        body = driver.find_element(By.ID, "BodyWrapper")
        main_content = body.find_element(By.ID, "MainContent")
        main_content_wrapper = main_content.find_element(By.ID, "MainContentWrapper")
        content_grid = main_content_wrapper.find_element(By.ID, "ContentGrid")
        try:
            screenshots_module = content_grid.find_element(By.ID, "ScreenshotsModule")
            img_element = screenshots_module.find_element(By.TAG_NAME, "img")
            self.img_url = img_element.get_attribute("src")
            print("Screenshot found")
        except:
            print("No screenshot found")

        try:
            updates_module = content_grid.find_element(By.ID, "UpdatesModule")
            version_element = updates_module.find_element(By.TAG_NAME, "small")
            self.version = version_element.text
            print("Version found")
        except:
            print("No version found")

    def run(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(defs.TIMEOUT_DURATION)

        try:
            driver.get(self.url)
        except TimeoutException:
            driver.execute_script("window.stop();")

        self.get_elements(driver)

        driver.close()
        self.callback(self.version, self.img_url)