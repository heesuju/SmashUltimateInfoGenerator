import threading
from typing import Union
import concurrent.futures
from src.utils.web import get_request
import difflib
import urllib.parse

WIFI_SAFE_TAGS = [
    "wifi safe",
    "wifi-safe",
    "wi-fi safe",
    "wifi_safe"
]

def get_mod_info(id:str):
    result = get_request(f"https://gamebanana.com/apiv4/Mod/{id}")
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

def get_mod_description(id:str):
    """
    Get mod description
    """
    try:
        GAMEBANANA_URL = "https://api.gamebanana.com/Core/Item/Data?\
            itemid={id}&\
            itemtype=Mod&\
            fields=text"
        url = GAMEBANANA_URL.format(id=id)
        data = get_request(url)
        return data[0]
    except Exception as e:
        print(f"Error getting mod description: {e}")
        return None

def search_mod(mod_name: str, author_name: str = "") -> str | None:
    """
    Search for a mod by name and optionally filter by author.
    Returns the Mod ID if found, else None.
    """
    try:
        encoded_name = urllib.parse.quote(mod_name)
        
        GAMEBANANA_SEARCH_URL = "https://gamebanana.com/apiv11/Util/Search/Results?\
            _sSearchString={query}&\
            _nPage=1&\
            _sModelName=Mod&\
            _sOrder=best_match&\
            _idGameRow=6498"
        url = GAMEBANANA_SEARCH_URL.format(query=encoded_name,
        author_name=author_name)
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
            return best_match
        
        records.sort(key=lambda x: x.get("_nViewCount", 0), reverse=True)
        if records:
            return records[0]
        return records
            
    except Exception as e:
        print(f"Error searching mod: {e}")
        return None
        
    return None

def search_mods_list(mod_name: str, author_name: str = "", page: int = 1, sort: str = "best_match") -> dict:
    """
    Search for mods and return a list of matches.
    
    Args:
        mod_name: Search query
        author_name: Optional author filter
        page: Page number (1-indexed)
        sort: Sort order - "best_match", "popularity", "date", or "udate"
    """
    try:
        encoded_name = urllib.parse.quote(mod_name)
        
        GAMEBANANA_SEARCH_URL = "https://gamebanana.com/apiv11/Util/Search/Results?\
            _sSearchString={query}&\
            _nPage={page}&\
            _sModelName=Mod&\
            _sOrder={sort}&\
            _idGameRow=6498"
        url = GAMEBANANA_SEARCH_URL.format(query=encoded_name, page=page, sort=sort)
        
        data = get_request(url)
        
        if not data:
            return {"records": [], "total_count": 0, "per_page": 15, "is_complete": True}
        
        # Extract metadata
        metadata = data.get("_aMetadata", {})
        total_count = metadata.get("_nRecordCount", 0)
        per_page = metadata.get("_nPerpage", 15)
        is_complete = metadata.get("_bIsComplete", True)
            
        records = data.get("_aRecords", [])
        
        # Filter by author if provided
        if author_name:
            filtered_records = []
            for record in records:
                submitter = record.get("_aSubmitter", {})
                submitter_name = submitter.get("_sName", "")
                if submitter_name and author_name.lower() in submitter_name.lower():
                    filtered_records.append(record)
            records = filtered_records
            
        return {
            "records": records,
            "total_count": total_count,
            "per_page": per_page,
            "is_complete": is_complete
        }
            
    except Exception as e:
        print(f"Error searching mod list: {e}")
        return {"records": [], "total_count": 0, "per_page": 15, "is_complete": True}

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
    def __init__(self, id:Union[str, list], callback:callable, is_search:bool=False, author_filter:str="", page:int=1, sort:str="best_match"):
        threading.Thread.__init__(self)
        self.id = id
        self.callback = callback
        self.is_search = is_search
        self.author_filter = author_filter
        self.page = page
        self.sort = sort
        self.daemon = True
        self.start()

    def run(self):
        results = []
        output_data = {}

        if self.is_search and isinstance(self.id, str):
            # Treat self.id as search query
            # If requesting a list (indicated by specific query or just general search usage)
            # For now, let's assume if it is a search, we might want a list if we are coming from OnlineManager
            # But the existing code expects a single result for "search_mod" call
            
            # We will use a convention: if page > 0, we want a list
            if self.page > 0:
                search_results = search_mods_list(self.id, self.author_filter, self.page, self.sort)
                # search_results is now a dict with records, total_count, per_page, is_complete
                # Pass the whole dict to callback
                self.callback(search_results)
                return
                # Convert list of dicts to standard format
                # We need to process each mod info partially since search results have limited data compared to full mod info
                # But search results usually have _idRow, _sName, _aPreviewMedia etc.
                
                final_list = []
                for record in search_results:
                    # Process record to extract key info
                    # Note: search records might differ slightly from full Get Item Data
                    # But process_mod_info expects certain structure.
                    # Search record keys: _idRow, _sName, _sProfileUrl, _aPreviewMedia, _aSubmitter etc.
                    
                    # Synthesize a data dict that process_mod_info can handle or extract manually
                    mod_id = str(record.get("_idRow", ""))
                    name = record.get("_sName", "")
                    submitter = record.get("_aSubmitter", {})
                    author = submitter.get("_sName", "") if submitter else ""
                    
                    # Preview handling for search records
                    previews = record.get("_aPreviewMedia", {}).get("_aImages", [])
                    thumb = ""
                    if previews:
                        # Get the first image object
                        image_obj = previews[0]
                        base_url = image_obj.get("_sBaseUrl", "")
                        
                        # Try to get a smaller file first (220px width seems good for grid)
                        # Fallback to 530, then 100, then original
                        file = image_obj.get("_sFile220", "")
                        if not file:
                            file = image_obj.get("_sFile530", "")
                        if not file:
                            file = image_obj.get("_sFile", "")
                            
                        if base_url and file:
                            thumb = f"{base_url}/{file}"
                    
                    final_list.append({
                        "id": mod_id,
                        "name": name,
                        "author": author,
                        "thumbnail": thumb,
                        "record": record # Keep raw record just in case
                    })
                
                self.callback(final_list)
                return

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
        elif isinstance(self.id, list):
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