import atexit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FireFoxOptions
import threading

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81"

class WebDriverSingleton:
    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def get_instance():
        if WebDriverSingleton._instance is None:
            with WebDriverSingleton._lock:
                if WebDriverSingleton._instance is None:
                    # Initialize WebDriver
                    try:
                        chrome_options = ChromeOptions()
                        chrome_options.add_argument("--headless=new")
                        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
                        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
                        chrome_options.add_experimental_option("useAutomationExtension", False) 
                        chrome_options.add_argument("--window-position=-2400,-2400") # Workaround for headless mode bug
                        chrome_options.add_argument(f"user-agent={USER_AGENT}")
                        WebDriverSingleton._instance = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
                        WebDriverSingleton._instance.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
                    except WebDriverException:
                        print("Chrome WebDriver not found, trying Firefox WebDriver.")
                        try:
                            firefox_options = FireFoxOptions()
                            firefox_options.add_argument("--headless")
                            firefox_options.add_argument(f"user-agent={USER_AGENT}")
                            WebDriverSingleton._instance = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
                        except WebDriverException:
                            print("No suitable WebDriver found.")
                            WebDriverSingleton._instance = None
                        
                    atexit.register(WebDriverSingleton._cleanup) # Cleanup on exit
        return WebDriverSingleton._instance
    
    @staticmethod
    def _cleanup():
        """Close the WebDriver when the program exits."""
        if WebDriverSingleton._instance is not None:
            WebDriverSingleton._instance.quit()  
            WebDriverSingleton._instance = None
            print("WebDriver closed on program exit.")