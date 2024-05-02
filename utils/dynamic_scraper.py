from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import defs
from threading import Thread

TIMEOUT_DELAY = 1

class Selenium(Thread):
    def __init__(self, url:str, callback):
        super().__init__()
        self.url = url
        self.callback = callback
        self.version = defs.DEFAULT_VERSION
        self.img_urls = []

    def run(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new") 
            chrome_options.add_argument("user-agent=fake-useragent")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(self.url)
            page_source = driver.execute_script("return document.body.outerHTML;")
            soup = BeautifulSoup(page_source, 'html.parser')
            self.img_urls = get_thumbnails(driver, soup)    
            self.version = get_version(driver, soup)
        except TimeoutException:
            driver.execute_script("window.stop();")
            print("driver timeout exception")
        finally:
            driver.close()
        
        self.callback(self.version, self.img_urls)

def get_thumbnails(driver, soup)->list[str]:
    thumbnails = []
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
        EC.presence_of_element_located((By.ID, "ScreenshotsModule"))
        )
        screenshots_module = soup.find('module', id="ScreenshotsModule")
        img_elements = screenshots_module.find_all('a')
        for e in img_elements:
            link = e.get('href')
            if link is not None and link not in thumbnails:
                thumbnails.append(link)
        print(f"{len(thumbnails)} thumbnails found")
    except TimeoutException:
        print("Thumbnails not found")
    finally:
        return thumbnails

def get_version(driver, soup)->str:
    version = defs.DEFAULT_VERSION
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
        EC.presence_of_element_located((By.ID, "UpdatesModule"))
        )
        updates_module = soup.find('module', id="UpdatesModule")
        version_element = updates_module.find("small")
        version = version_element.text
        print(f"Version: {version}")
    except:
        print("Version not found")
    finally:
        return version