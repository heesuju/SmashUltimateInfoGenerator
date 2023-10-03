import requests
from bs4 import BeautifulSoup
import re

class Extractor:
    def __init__(self):
        self.url = ""
        self.mod_title = ""
        self.authors = ""
        self.result = False

    def get_elements(self, url):
        if self.url != url:
            self.url = url
            soup = self.get_html(self.url)
            if soup:
                self.mod_title = self.get_mod_title(soup)
                self.authors = self.get_authors(soup)
                self.result = True
            else:
                self.mod_title = ""
                self.authors = ""
                self.result = False 
        return self.result, self.mod_title, self.authors
            
    def get_html(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup
            else:
                print("Failed to retrieve the web page. Status code:", response.status_code)
                return None
        except Exception as e:
            print("An error occurred:", str(e))
            return None
        
    def get_mod_title(self, soup):
        page_title = ""
        page_title_h1 = soup.find('h1', id="PageTitle")

        if page_title_h1:
            page_title = page_title_h1.contents[0].get_text().replace("\t", "").replace("\n", "")
            print(page_title)
        return page_title
    
    def get_authors(self, soup):
        result = ""
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            description_content = meta_description.get('content') 
            pattern = r'submitted by (.+)$'
            match = re.search(pattern, description_content)

            if match:
                result = match.group(1)
            else:
                print("Authors not found in the text.")   
        return result.replace(" and", ",")