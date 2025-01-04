from typing import List
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

TIMEOUT_DELAY = 1

def get_thumbnails(driver) -> List[str]:
    thumbnails = []
    descriptions = []
    
    try:
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
            EC.presence_of_element_located((By.ID, "ScreenshotsModule"))
        )

        # Use Selenium to find the images directly
        img_elements = driver.find_elements(By.CSS_SELECTOR, "#ScreenshotsModule a")
        
        for e in img_elements:
            link = e.get_attribute('href')  # Get the href attribute (image URL)
            img = e.find_element(By.TAG_NAME, 'img')  # Get the <img> tag inside the <a>
            desc = img.get_attribute('alt') if img else ""  # Get the alt text of the image
            
            if link and link not in thumbnails:
                thumbnails.append(link)
                descriptions.append(desc)

        print(f"{len(thumbnails)} thumbnails found")
        
    except TimeoutException:
        print("Thumbnails not found")

    except Exception as e:
        print("Unknown Exception:", e)
        
    finally:
        # Return both the thumbnails and processed descriptions (number_dups logic is assumed)
        return thumbnails, handle_duplicates(descriptions)
        
def handle_duplicates(descriptions:List[str])->List[str]:
    inputs = [desc if desc else "untitled" for desc in descriptions]
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