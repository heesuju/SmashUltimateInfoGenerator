import atexit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import threading

class WebDriverSingleton:
    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def get_instance():
        if WebDriverSingleton._instance is None:
            with WebDriverSingleton._lock:
                if WebDriverSingleton._instance is None:
                    # Initialize WebDriver
                    chrome_options = Options()
                    chrome_options.add_argument("--headless=new")
                    chrome_options.add_argument("--window-position=-2400,-2400") # Workaround for headless mode bug
                    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81"
                    chrome_options.add_argument(f"user-agent={user_agent}")

                    WebDriverSingleton._instance = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
                    atexit.register(WebDriverSingleton._cleanup) # Cleanup on exit
        return WebDriverSingleton._instance
    
    @staticmethod
    def _cleanup():
        """Close the WebDriver when the program exits."""
        if WebDriverSingleton._instance is not None:
            WebDriverSingleton._instance.quit()  
            WebDriverSingleton._instance = None
            print("WebDriver closed on program exit.")