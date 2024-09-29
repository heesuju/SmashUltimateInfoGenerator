from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import defs
from threading import Thread
from typing import List
from utils.classify_mod_safety import classify_mod_safety

TIMEOUT_DELAY = 1
PUNCTUATIONS = [".", "?", "!"]

class Selenium(Thread):
    def __init__(self, url:str, callback):
        super().__init__()
        self.url = url
        self.callback = callback
        self.version = defs.DEFAULT_VERSION
        self.img_urls = []
        self.img_descriptions = []

    def run(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81"
            chrome_options.add_argument(f"user-agent={user_agent}")

            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
            driver.get(self.url)
            page_source = driver.execute_script("return document.body.outerHTML;")
            soup = BeautifulSoup(page_source, 'html.parser')
            # is_nsfw = check_if_nsfw(driver, soup)
            self.img_urls, self.img_descriptions = get_thumbnails(driver, soup)    
            self.version = get_version(driver, soup)
            wifi_safe = get_wifi_safety(driver, soup)
        except TimeoutException:
            driver.execute_script("window.stop();")
            print("driver timeout exception")
        finally:
            driver.close()
        
        self.callback(self.version, self.img_urls, self.img_descriptions, wifi_safe)

def check_if_nsfw(driver, soup):
    result = False
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
        EC.presence_of_element_located((By.ID, "ContentWarningModule"))
        )
        content_warning = soup.find('module', id="ContentWarningModule")
        print(f"not safe for work")
        result = True
    except TimeoutException:
        print("no nsfw content found")
        result = False
    finally:
        return result

def get_thumbnails(driver, soup)->List[str]:
    thumbnails = []
    descriptions = []
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
        EC.presence_of_element_located((By.ID, "ScreenshotsModule"))
        )
        screenshots_module = soup.find('module', id="ScreenshotsModule")
        img_elements = screenshots_module.find_all('a')
        for e in img_elements:
            link = e.get('href')
            alts = e.find_all('img')
            desc = alts[0].get('alt') if len(alts) > 0 else ""
            
            if link is not None and link not in thumbnails:
                thumbnails.append(link)
                descriptions.append(desc)

        print(f"{len(thumbnails)} thumbnails found")
    except TimeoutException:
        print("Thumbnails not found")
    finally:
        return thumbnails, number_dups(descriptions)

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
    
def number_dups(descriptions:List[str])->List[str]:
    inputs = [desc if desc is not None else "untitled" for desc in descriptions]
    outputs = []
    name_dict = {}
    
    for n in inputs:
        if n in name_dict.keys():
            name_dict[n] += 1
            outputs.append(n + " " + str(name_dict[n]))
        else: 
            name_dict[n] = 1
            outputs.append(n)
    
    return outputs

def get_wifi_safety(driver, soup)->str:
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        parts = [x for x in text.split("\n") if x]
        text = "\n".join(parts)
        result = classify_mod_safety(text)
        print("Wifi-safe:", result)
        return result
    except TimeoutException:
        print("Failed to find body")
        return "Uncertain"