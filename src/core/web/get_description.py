from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.core.formatting import clean_description

TIMEOUT_DELAY = 1
DEFAULT_VERSION = "1.0.0"

def get_description(driver)->str:
    description = ""
    
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
            EC.presence_of_element_located((By.ID, "ItemProfileModule"))
        )

        profile_module = driver.find_element(By.ID, "ItemProfileModule")
        articles = profile_module.find_element(By.TAG_NAME, "article")
        description = articles.text
        description = clean_description(description)
        print(description)

    except TimeoutException:
        print("Description not found")
        
    finally:
        return description