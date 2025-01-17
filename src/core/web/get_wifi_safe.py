import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

TIMEOUT_DELAY = 1

POSITIVE_PATTERNS = [
    r"wi[-\s]?fi[-\s]?safe", 
    r"safe\sfor\swifi", 
    r"compatible\swith\sonline\splay",
    r"tested\sfor\smultiplayer",
    r"works\swell\sover\sWiFi"
]

NEGATIVE_PATTERNS = [
    r"not\s+wi[-\s]?fi[-\s]?safe", 
    r"may\scause\sdesyncs", 
    r"not\srecommended\sfor\smultiplayer", 
    r"can\sget\syou\sbanned", 
    r"incompatible\swith\sonline",
    r"do\snot\suse\sonline",
    r"unsafe\sfor\sonline\splay"
]

NEGATION_PATTERNS = [
    r"(not|do\snot)\s+\w+\s+wi[-\s]?fi[-\s]?safe",
    r"(not|do\snot)\s+recommend\sonline\suse",
    r"(not|do\snot)\s+work\sover\sWiFi"
]

def get_wifi_safe(driver) -> str:
    try:
        # Wait for the body tag to be present
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        body_element = driver.find_element(By.TAG_NAME, "body")
        text = body_element.text  # Extract the full text content of the body
        
        parts = [x for x in text.split("\n") if x.strip()]
        clean_text = "\n".join(parts)
        
        # Use your classification function to determine wifi safety
        result = classify_mod_safety(clean_text)
        print("Wifi-safe:", result)
        return result

    except TimeoutException:
        print("Failed to find body")
        return "Uncertain"
    
def get_wifi_safe_tag(driver) -> bool:
    try:
        # Wait for the body tag to be present
        wrapper = WebDriverWait(driver, TIMEOUT_DELAY).until(
            EC.presence_of_element_located((By.ID, "TagsModule"))
        )
        
        tag_module = driver.find_element(By.ID, "TagsModule")
        items = tag_module.find_elements(By.TAG_NAME, "a")
        for item in items:
            href = item.get_attribute("href")
            if "wifi%20safe+safe+yes" in href or "Wifi%20Safe" in href:
                return True

    except TimeoutException:
        print("Failed to find body")
    
    return False
    
# Rule-based classification
def classify_mod_safety(text)->str:
    score = 0
    
    if find_positive_patterns(text):
        score += 1
    
    if find_negative_patterns(text):
        score -= 1
    
    if find_negations(text):
        score -= 1

    if score > 0:
        return "Safe"
    elif score < 0:
        return "Not Safe"
    else:
        return "Uncertain"

# Function to check for positive patterns
def find_positive_patterns(text):
    for pattern in POSITIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Function to check for negative patterns
def find_negative_patterns(text):
    for pattern in NEGATIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Function to check for negations near "wifi-safe"
def find_negations(text):
    for pattern in NEGATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False