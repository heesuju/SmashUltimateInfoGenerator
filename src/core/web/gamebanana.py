import threading
from typing import Union
import concurrent.futures
from src.utils.web import get_request
from src.constants.api import GAMEBANANA_URL

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
    def __init__(self, id:Union[str, list], callback:callable):
        threading.Thread.__init__(self)
        self.id = id
        self.callback = callback
        self.daemon = True
        self.start()

    def run(self):
        results = []
        output_data = {}

        if isinstance(self.id, str):
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