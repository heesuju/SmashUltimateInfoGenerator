from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from defs import DEFAULT_VERSION
from utils.cleaner import clean_vesion

TIMEOUT_DELAY = 1

def get_nsfw(driver)->str:
    result = False
    
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
            EC.presence_of_element_located((By.ID, "ContentWarningModule"))
        )

        content_warning = driver.find_element(By.ID, "ContentWarningModule")
        result = True
        print("Mod is not safe for work")

    except TimeoutException:
        print("Mod is safe for work")
        
    finally:
        return result