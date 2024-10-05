from ui.config import load_config
from .cleaner import clean_folder_name, clean_display_name

def format_display_name(characters:str, slots:str, mod_name:str, category:str):
    format = load_config().get("display_name_format")
    display_name = format.replace("{characters}", characters)
    display_name = display_name.replace("{slots}", slots)
    display_name = display_name.replace("{mod}", mod_name)
    display_name = display_name.replace("{category}", category)
    return clean_display_name(display_name)

def format_folder_name(characters:str, slots:str, mod_name:str, category:str):
    format = load_config().get("folder_name_format")
    folder_name = format.replace("{characters}", characters)
    folder_name = folder_name.replace("{slots}", slots)
    folder_name = folder_name.replace("{mod}", mod_name)
    folder_name = folder_name.replace("{category}", category)
    return clean_folder_name(folder_name)

def format_slots(slots):
    if len(slots) <= 0:
        return ""
    
    ranges = []
    current_idx = 0
    out_str = ""
    start = slots[0] 
    prev = slots[0]
    if not isinstance(start,int):
        ranges.append(start)
    else:
        ranges.append(f"{start:02}")

        for n in range(1, len(slots)):
            if prev + 1 == slots[n]:
                ranges[current_idx] = f"{start:02}" + "-" + f"{slots[n]:02}"
            else:
                current_idx+=1
                ranges.append(f"{slots[n]:02}")
                start = slots[n]
            prev = slots[n]

    for item in ranges:
        if not out_str:
            out_str += item
        else:
            out_str += "," + item
    
    slot_prefix = "C"
    loaded_config = load_config()
    if loaded_config is not None:
        is_cap = loaded_config.get("is_slot_capped")
        if is_cap == False:
            slot_prefix = "c"
            
    return slot_prefix + out_str