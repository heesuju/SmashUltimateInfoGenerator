
def sort_by_priority(mods, priority:list):
    if priority is None or len(priority) == 0:
        return mods
    
    def get_sort_key(x):
        sort_key = []
        for p in priority:
            col_value = x[p["column"]]
            sort_key.append(col_value)
        return tuple(sort_key)
    
    reverse_flags = [p["order"] == "Descending" for p in priority]
    
    sorted_data = sorted(mods, key=get_sort_key, reverse=any(reverse_flags))    
    return sorted_data