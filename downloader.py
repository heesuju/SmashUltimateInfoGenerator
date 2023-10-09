from threading import Thread
import requests
import defs

class Downloader(Thread):
    def __init__(self, url:str, dir:str, callback):
        super().__init__()
        self.url = url
        self.dir = dir
        self.callback = callback

    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Check for any HTTP errors
            file_name = self.dir + "/" + defs.IMAGE_NAME 
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded and saved as {defs.IMAGE_NAME}")
            self.callback()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")