import webbrowser
import re

def trim_url(url:str)->str:
    parts = url.split("/")
    return parts[-1]

def open_page(url:str):
    webbrowser.open(url)

def is_valid_url(url):
    pattern = r'https://gamebanana\.com/.*/\d+'
    
    if re.match(pattern, url):
        print("Valid url")
        return True
    else:
        print("Invalid url")
        return False