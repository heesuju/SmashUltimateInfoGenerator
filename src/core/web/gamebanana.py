import threading
from typing import Union
import concurrent.futures
from src.utils.web import get_request
from src.constants.apis import GAMEBANANA_URL, GAMEBANANA_SEARCH_URL
import difflib
import urllib.parse

WIFI_SAFE_TAGS = [
    "wifi safe",
    "wifi-safe",
    "wi-fi safe",
    "wifi_safe"
]

def get_mod_info(id:str):
    url = GAMEBANANA_URL.format(id)
    result = get_request(url)
    return result

def get_thumbnails(data:dict)->tuple[list[str], list[str]]:
    links, file_names = [], []
    
    previews = data.get("_aPreviewMedia", None)
    for preview in previews:
        file_type = preview.get("_sType", None)
        if file_type is not None and file_type == "image":
            file_name = preview.get("_sFile", "")
            if file_name:
                link = f'{preview.get("_sBaseUrl", "")}/{file_name}'
                if link not in links:
                    links.append(link)
                    file_names.append(file_name)
    
    return links, file_names

def search_mod(mod_name: str, author_name: str = "") -> str | None:
    """
    Search for a mod by name and optionally filter by author.
    Returns the Mod ID if found, else None.
    """
    try:
        encoded_name = urllib.parse.quote(mod_name)
        url = GAMEBANANA_SEARCH_URL.format(encoded_name)
        data = get_request(url)
        
        if not data or not data.get("_aRecords"):
            return None
            
        records = data.get("_aRecords", [])
        
        # If no author provided, fallback to view count
        if not author_name:
            # Sort by view count descending
            records.sort(key=lambda x: x.get("_nViewCount", 0), reverse=True)
            if records:
                return str(records[0].get("_idRow"))
            return None
            
        # If author provided, try fuzzy match
        best_match = None
        best_ratio = 0.0
        
        for record in records:
            submitter = record.get("_aSubmitter", {})
            submitter_name = submitter.get("_sName", "")
            
            if not submitter_name:
                continue
                
            ratio = difflib.SequenceMatcher(None, author_name.lower(), submitter_name.lower()).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = record
        
        # Threshold for match? Let's say 0.4 to be lenient
        if best_match and best_ratio > 0.4:
            return str(best_match.get("_idRow"))
        
        records.sort(key=lambda x: x.get("_nViewCount", 0), reverse=True)
        if records:
            return str(records[0].get("_idRow"))
            
    except Exception as e:
        print(f"Error searching mod: {e}")
        return None
        
    return None

def process_mod_info(data:dict)->tuple[str, dict]:
    profile = data.get("_sProfileUrl", "")
    id = profile.split("/")[-1]
    mod_name = data.get("_sName", "")
    additional_info = data.get("_aAdditionalInfo", None)
    version = "1.0.0"
    if additional_info is not None:
        version = additional_info.get("_sVersion", "")
    submitter = data.get("_aSubmitter", None)
    authors = ""
    if submitter is not None:
        authors = submitter.get("_sName", "")
    preview_links, preview_files = get_thumbnails(data)
    category = data.get("_aCategory", None)
    is_final_smash = False
    is_nsfw = data.get("_bIsNsfw", False)
    is_moveset = False
    if category is not None:
        if category.get("_sName") == "Final Smash":
            is_final_smash = True
        elif category.get("_sName") == "Movesets":
            is_moveset = True

    super_category = data.get("_aSuperCategory", None)
    if super_category is not None:
        if super_category.get("_sName") == "Final Smash":
            is_final_smash = True
        elif super_category.get("_sName") == "Movesets":
            is_moveset = True

    attributes = data.get("_aAttributes", None)
    is_wifi_safe = False
    if attributes is not None:
        if isinstance(attributes, dict):
            misc = attributes.get("Miscellaneous", [])
            if "Wifi Safe" in misc:
                is_wifi_safe = True

            if is_wifi_safe == False:
                for tag in WIFI_SAFE_TAGS:
                    wifi_safe = attributes.get(tag, [])
                    if "yes" in wifi_safe:
                        is_wifi_safe = True
                        break

    return id, {
        "mod_name": mod_name, 
        "version":version, 
        "authors":authors, 
        "preview_links":preview_links, 
        "preview_files":preview_files,
        "is_moveset":is_moveset,
        "is_final_smash":is_final_smash,
        "is_nsfw":is_nsfw,
        "is_wifi_safe":is_wifi_safe
    }

class Gamebanana(threading.Thread):
    def __init__(self, id:Union[str, list], callback:callable, is_search:bool=False, author_filter:str=""):
        threading.Thread.__init__(self)
        self.id = id
        self.callback = callback
        self.is_search = is_search
        self.author_filter = author_filter
        self.daemon = True
        self.start()

    def run(self):
        results = []
        output_data = {}

        if self.is_search and isinstance(self.id, str):
            # Treat self.id as search query
            found_id = search_mod(self.id, self.author_filter)
            if found_id:
                # Proceed to fetch info for the found ID
                result = get_mod_info(found_id)
                if result is not None:
                    results.append(result)
        elif isinstance(self.id, str):
            result = get_mod_info(self.id)
            if result is not None:
                results.append(result)
        elif isinstance(self.id, list[str]):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_mod_info, id) for id in self.id]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result is not None:
                        results.append(result)
        
        if len(results) > 0:
            for r in results:
                key, value = process_mod_info(r)
                output_data[key] = value

        self.callback(output_data)