import threading
import re
from typing import Union
import concurrent.futures
from src.utils.web import get_request
import difflib
import urllib.parse
from src.constants.apis import ApiEndpoints

WIFI_SAFE_TAGS = [
    "wifi safe",
    "wifi-safe",
    "wi-fi safe",
    "wifi_safe"
]

POSITIVE_PATTERNS = [
    re.compile(r"wi[-\s]?fi[-\s]?safe", re.IGNORECASE), 
    re.compile(r"safe\sfor\swifi", re.IGNORECASE), 
    re.compile(r"compatible\swith\sonline\splay", re.IGNORECASE), 
    re.compile(r"tested\sfor\smultiplayer", re.IGNORECASE), 
    re.compile(r"works\swell\sover\sWiFi", re.IGNORECASE)
]

NEGATIVE_PATTERNS = [
    re.compile(r"not\s+wi[-\s]?fi[-\s]?safe", re.IGNORECASE), 
    re.compile(r"may\scause\sdesyncs", re.IGNORECASE), 
    re.compile(r"not\srecommended\sfor\smultiplayer", re.IGNORECASE), 
    re.compile(r"can\sget\syou\sbanned", re.IGNORECASE), 
    re.compile(r"incompatible\swith\sonline", re.IGNORECASE), 
    re.compile(r"do\snot\suse\sonline", re.IGNORECASE), 
    re.compile(r"unsafe\sfor\sonline\splay", re.IGNORECASE)
]

NEGATION_PATTERNS = [
    re.compile(r"(not|do\snot)\s+\w+\s+wi[-\s]?fi[-\s]?safe", re.IGNORECASE),
    re.compile(r"(not|do\snot)\s+recommend\sonline\suse", re.IGNORECASE),
    re.compile(r"(not|do\snot)\s+work\sover\sWiFi", re.IGNORECASE)
]

# Rule-based classification
def classify_mod_safety(text)->str:
    score = 0
    
    if find_positive_patterns(text):
        score += 1
    
    if find_negative_patterns(text):
        score -= 1
    
    if find_negations(text):
        score -= 1

    if score > 0:
        return "Safe"
    elif score < 0:
        return "Not Safe"
    else:
        return "Uncertain"

# Function to check for positive patterns
def find_positive_patterns(text):
    for pattern in POSITIVE_PATTERNS:
        if pattern.search(text):
            return True
    return False

# Function to check for negative patterns
def find_negative_patterns(text):
    for pattern in NEGATIVE_PATTERNS:
        if pattern.search(text):
            return True
    return False

# Function to check for negations near "wifi-safe"
def find_negations(text):
    for pattern in NEGATION_PATTERNS:
        if pattern.search(text):
            return True
    return False

def get_mod_info(id:str):
    url = ApiEndpoints.GAMEBANANA_MOD_DATA.format(id=id)
    result = get_request(url)
    return result

def get_thumbnails(data:dict)->tuple[list[str], list[str]]:
    links, file_names = [], []
    
    previews = data.get("_aPreviewMedia", None)
    if isinstance(previews, dict):
        previews = previews.get("_aImages", [])
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
        url = ApiEndpoints.GAMEBANANA_MOD_DESCRIPTION.format(id=id)
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
        url = ApiEndpoints.GAMEBANANA_MOD_SEARCH_BY_BEST_MATCH.format(query=encoded_name)
        data = get_request(url)
        
        if not data or not data.get("_aRecords"):
            return None
            
        records = data.get("_aRecords", [])
        
        # If no author provided, fallback to view count
        if not author_name:
            if records:
                return records[0]
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
        url = ApiEndpoints.GAMEBANANA_MOD_SEARCH_LIST.format(query=encoded_name, page=page, sort=sort)
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

def get_new_mods(page: int = 1) -> list:
    """
    Get new/updated mods.
    """
    try:
        url = ApiEndpoints.GAMEBANANA_MOD_NEW_LIST.format(page=page)
        data = get_request(url)
        if not data:
            return []
        
        # The API returns a list of [["Mod", id], ...], we need to extract IDs
        ids = []
        for item in data:
            if isinstance(item, list) and len(item) >= 2 and item[0] == "Mod":
                ids.append(item[1])
        return ids
    except Exception as e:
        print(f"Error getting new mods: {e}")
        return []

def search_users(name: str) -> list[int]:
    """
    Search for users by name.
    Returns a list of user IDs.
    """
    try:
        url = ApiEndpoints.GAMEBANANA_USER_SEARCH.format(name=urllib.parse.quote(name))
        data = get_request(url)
        if not data:
            return []
        
        ids = []
        for item in data:
            if isinstance(item, dict) and "id" in item:
                ids.append(item["id"])
        return ids
    except Exception as e:
        print(f"Error searching users: {e}")
        return []

def get_new_mods_by_user(user_id: int, page: int = 1) -> list[int]:
    """
    Get new mods by user ID.
    """
    try:
        url = ApiEndpoints.GAMEBANANA_MOD_NEW_LIST_BY_USER.format(page=page, user=user_id)
        data = get_request(url)
        if not data:
            return []
        
        ids = []
        for item in data:
            if isinstance(item, list) and len(item) >= 2 and item[0] == "Mod":
                ids.append(item[1])
        return ids
    except Exception as e:
        print(f"Error getting new mods by user: {e}")
        return []

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

    files = []
    a_files = data.get("_aFiles", [])
    if a_files:
        for f in a_files:
            file_entry = {
                "name": f.get("_sFile", ""),
                "url": f.get("_sDownloadUrl", ""),
                "description": f.get("_sDescription", "")
            }
            if file_entry["name"] and file_entry["url"]:
                files.append(file_entry)

    return id, {
        "mod_name": mod_name, 
        "version":version, 
        "authors":authors, 
        "preview_links":preview_links, 
        "preview_files":preview_files,
        "is_moveset":is_moveset,
        "is_final_smash":is_final_smash,
        "is_nsfw":is_nsfw,
        "is_wifi_safe":is_wifi_safe,
        "files": files
    }

class Gamebanana(threading.Thread):
    def __init__(self, id:Union[str, list], callback:callable, is_search:bool=False, is_new:bool=False, author_filter:str="", page:int=1, sort:str="best_match"):
        threading.Thread.__init__(self)
        self.id = id
        self.callback = callback
        self.is_search = is_search
        self.is_new = is_new
        self.author_filter = author_filter
        self.page = page
        self.sort = sort
        self.daemon = True
        self.start()

    def run(self):
        results = []
        output_data = {}

        if self.is_new:
            ids = []
            
            if self.author_filter:
                user_ids = search_users(self.author_filter)
                
                if user_ids:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        futures = [executor.submit(get_new_mods_by_user, uid, self.page) for uid in user_ids]
                        for future in concurrent.futures.as_completed(futures):
                            u_ids = future.result()
                            if u_ids:
                                ids.extend(u_ids)
            else:
                ids = get_new_mods(self.page)
                
            if not ids:
                self.callback({"records": [], "total_count": 0, "per_page": 0, "is_complete": True})
                return

            fetched_records = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(get_mod_info, str(mod_id)) for mod_id in ids]
                
                for future in futures:
                    try:
                        result = future.result()
                        if result:
                            # Adapter: Standardize v4 response to match v11 (Search) structure
                            
                            # 1. Ensure _idRow
                            if "_idRow" not in result:
                                profile = result.get("_sProfileUrl", "")
                                if profile:
                                    try:
                                        result["_idRow"] = int(profile.split("/")[-1])
                                    except:
                                        pass
                            
                            # 2. Map Category (_aSuperCategory -> _aRootCategory)
                            if "_aRootCategory" not in result:
                                # v4 has _aSuperCategory (e.g. "Skins") and _aCategory (e.g. "Person")
                                # OnlineManager checks _aRootCategory._sName
                                result["_aRootCategory"] = result.get("_aSuperCategory") or result.get("_aCategory")

                            # 3. Lift Version
                            if "_sVersion" not in result and "_aAdditionalInfo" in result:
                                result["_sVersion"] = result["_aAdditionalInfo"].get("_sVersion", "")

                            # 4. Standardize Preview Media (List -> Dict wrapper)
                            # v4 returns a list of images directly in _aPreviewMedia
                            # v11 returns dict with _aImages key
                            pm = result.get("_aPreviewMedia")
                            if isinstance(pm, list):
                                result["_aPreviewMedia"] = {"_aImages": pm}

                            fetched_records.append(result)
                    except Exception as e:
                        print(f"Error fetching mod details: {e}")
            
            output = {
                "records": fetched_records,
                "total_count": 1000, 
                "per_page": len(ids),
                "is_complete": False
            }
            self.callback(output)
            return

        if self.is_search and isinstance(self.id, str):
            # Treat self.id as search query
            if self.page > 0:
                search_results = search_mods_list(self.id, self.author_filter, self.page, self.sort)
                self.callback(search_results)
                return

            found_id = search_mod(self.id, self.author_filter)
            if found_id:
                # Proceed to fetch info for the found ID
                result = get_mod_info(found_id)
                if result is not None:
                    results.append(result)
        elif isinstance(self.id, str):
            # Direct ID fetch
            result = get_mod_info(self.id)
            if result is not None:
                results.append(result)
        elif isinstance(self.id, list):
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(get_mod_info, id) for id in self.id]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result is not None:
                        results.append(result)
        
        # Process results
        if len(results) > 0:
            if len(results) == 1:
                # Single result - process full info
                key, value = process_mod_info(results[0])
                # Add description which process_mod_info doesn't currently get
                desc = get_mod_description(key)
                if desc:
                    value['description'] = desc
                    
                    if value.get("is_wifi_safe", False) == False:
                        classification = classify_mod_safety(desc)
                        if classification == "Safe":
                            value['is_wifi_safe'] = True

                # Wrap in dict keyed by ID
                output_data[key] = value
            else:
                for r in results:
                    key, value = process_mod_info(r)
                    output_data[key] = value

        self.callback(output_data)