"""
web.py: Contains various methods related to web browsing
"""

import webbrowser
import re

def trim_url(url:str)->str:
    """
    Used to get the image name when downloading thumbnails from gamebanana
    Returns the lasts part of the url string
    """
    parts = url.split("/")
    return parts[-1]

def open_page(url:str)->None:
    """
    Opens the url webpage
    """
    webbrowser.open(url)

def is_valid_url(url)->bool:
    """
    Checks if the given url is a gamebanana page
    Returns true or false
    """

    url_pattern = r'https://gamebanana\.com/.*/\d+'

    if re.match(url_pattern, url):
        print("Valid url")
        return True
    else:
        print("Invalid url")
        return False
