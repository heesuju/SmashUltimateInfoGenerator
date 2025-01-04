from threading import Thread
import requests

class Downloader(Thread):
    def __init__(self, url:str, dir:str, callback=None):
        super().__init__()
        self.url = url
        self.dir = dir
        self.callback = callback

    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Check for any HTTP errors
            with open(self.dir, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded and saved in {self.dir}")
            if self.callback is not None:
                self.callback()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")