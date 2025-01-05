"""
downloader.py: downloads the selected file in another thread
"""

from threading import Thread
import requests

TIMEOUT = 10

class Downloader(Thread):
    """
    Class that inherits from thread
    Downloads the file from the web into the specified directory
    """
    def __init__(self, url:str, directory:str, callback=None):
        super().__init__()
        self.url = url
        self.directory = directory
        self.callback = callback

    def run(self):
        try:
            response = requests.get(self.url, timeout=TIMEOUT)
            response.raise_for_status()  # Check for any HTTP errors
            with open(self.directory, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded and saved in {self.directory}")
            if self.callback is not None:
                self.callback()
        except TimeoutError:
            print("download request timed out")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
