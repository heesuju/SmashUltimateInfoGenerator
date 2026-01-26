"""
Contains definitions api endpoints
"""

class ApiEndpoints:
    GAMEBANANA_MOD_DESCRIPTION = "https://api.gamebanana.com/Core/Item/Data?itemid={id}&itemtype=Mod&fields=text"
    GAMEBANANA_MOD_SEARCH_BY_BEST_MATCH = "https://gamebanana.com/apiv11/Util/Search/Results?_sSearchString={query}&_nPage=1&_sModelName=Mod&_sOrder=best_match&_idGameRow=6498"
    GAMEBANANA_MOD_SEARCH_LIST = "https://gamebanana.com/apiv11/Util/Search/Results?_sSearchString={query}&_nPage={page}&_sModelName=Mod&_sOrder={sort}&_idGameRow=6498"
    GAMEBANANA_MOD_NEW_LIST = "https://api.gamebanana.com/Core/List/New?itemtype=Mod&gameid=6498&include_updated=1&page={page}"
    GAMEBANANA_MOD_DATA = "https://gamebanana.com/apiv4/Mod/{id}"