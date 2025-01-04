from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.utils.string_helper import clean_vesion

TIMEOUT_DELAY = 1
DEFAULT_VERSION = "1.0.0"

def get_version(driver)->str:
    version = DEFAULT_VERSION
    
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
            EC.presence_of_element_located((By.ID, "UpdatesModule"))
        )

        updates_module = driver.find_element(By.ID, "UpdatesModule")
        version_element = updates_module.find_element(By.TAG_NAME, "small")
        version = clean_vesion(version_element.text)
        print("Version found:", version)

    except TimeoutException:
        print("Version not found")
        
    finally:
        return version