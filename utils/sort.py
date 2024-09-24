
def sort_by_priority(mods, priority:list):
    if priority is None:
        return mods
    
    if len(priority) >= 4:
        sorted_data = sorted(mods, key=lambda x: (x[priority[0]["column"]] if priority[0]["order"] == "Ascending" else ''.join(reversed(x[priority[0]["column"]])), 
                                              x[priority[1]["column"]] if priority[1]["order"] == "Ascending" else ''.join(reversed(x[priority[1]["column"]])),
                                              x[priority[2]["column"]] if priority[2]["order"] == "Ascending" else ''.join(reversed(x[priority[2]["column"]])),
                                              x[priority[3]["column"]] if priority[3]["order"] == "Ascending" else ''.join(reversed(x[priority[3]["column"]]))))
    
    elif len(priority) >= 3:
        sorted_data = sorted(mods, key=lambda x: (x[priority[0]["column"]] if priority[0]["order"] == "Ascending" else ''.join(reversed(x[priority[0]["column"]])), 
                                              x[priority[1]["column"]] if priority[1]["order"] == "Ascending" else ''.join(reversed(x[priority[1]["column"]])),
                                              x[priority[2]["column"]] if priority[2]["order"] == "Ascending" else ''.join(reversed(x[priority[2]["column"]]))))
        
    elif len(priority) >= 2:
        sorted_data = sorted(mods, key=lambda x: (x[priority[0]["column"]] if priority[0]["order"] == "Ascending" else ''.join(reversed(x[priority[0]["column"]])), 
                                              x[priority[1]["column"]] if priority[1]["order"] == "Ascending" else ''.join(reversed(x[priority[1]["column"]]))))
        
    elif len(priority) >= 1:
        sorted_data = sorted(mods, key=lambda x: (x[priority[0]["column"]] if priority[0]["order"] == "Ascending" else ''.join(reversed(x[priority[0]["column"]]))))
    
    return sorted_data