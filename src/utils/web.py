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

# from duckduckgo_search import DDGS

# # Function to search DuckDuckGo
# def search_duckduckgo(query:str, max_results=10):
#     with DDGS() as ddgs:  # No proxy used
#         results = ddgs.text(query, max_results=max_results)
#         return results
    
import requests

def get_request(url:str, params:dict=None):
    """
    Makes HTTP GET request to the specified URL with optional parameters.
    
    :param url: The target URL.
    :param params: A dictionary of query parameters (optional).
    :return: The response JSON or text, or an error message.
    """
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Try to return JSON response, otherwise return text
        try:
            return response.json()
        except requests.JSONDecodeError:
            print(response.text)
            return None
        
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.ConnectionError:
        return "Error: Unable to connect to the server."
    except requests.exceptions.Timeout:
        return "Error: The request timed out."
    except requests.exceptions.RequestException as err:
        return f"An error occurred: {err}"