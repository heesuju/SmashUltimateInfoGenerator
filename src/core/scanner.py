import os
from src.utils.file import (
    is_valid_dir, 
    is_valid_file,
    get_children, 
    search_dir_by_keyword, 
    get_direct_child_by_extension, 
    get_children_by_extension, 
    search_files_for_pattern
)
from src.utils.csv_helper import csv_to_dict
from src.utils.string_helper import str_to_int
from src.models.mod import Mod
from src.constants.elements import *
from src.constants.categories import *
from .formatting import (
    format_slots,
    get_mod_name,
    format_character_names,
    group_char_name
)
from data import PATH_CHAR_NAMES

def scan_character(root_dir:str, subfolders:list[str], mod:Mod, is_fighter:bool=True)->Mod:

    def get_slots_as_number(slots:list[str])->list[int]:
        numbers = []

        for s in slots:
            numbers.append(str_to_int(s, 1))

        numbers.sort()
        return numbers

    character_dict = csv_to_dict(PATH_CHAR_NAMES)
    keys, names, groups, slots = [], [], [], []

    if len(subfolders) > 1 and "kirby" in subfolders:
        subfolders.remove("kirby")

    for child in subfolders:
        for dict in character_dict:
            if child != dict['Key']:
                continue

            keys.append(dict['Key'])
            names.append(dict['Custom'])
            groups.append(dict['Group'])
            tmp_slots = []

            if not is_fighter:
                path = os.path.join(root_dir, "fighter", child)
                all_slots = get_direct_child_by_extension(path, ".eff")
                for file_name in all_slots:
                    tmp_slots = get_slots_as_number(file_name)
                    for s in tmp_slots:
                        if s not in slots:
                            slots.append(s)
            else:
                path = os.path.join(root_dir, child)
                model_dir = os.path.join(path, "model")
                if is_valid_dir(model_dir):
                    models = get_children(model_dir)

                    for model in models:
                        slot_strings = get_children(os.path.join(model_dir, model))
                        tmp_slots = get_slots_as_number(slot_strings)
                        for slot in tmp_slots:
                            if slot not in slots:
                                slots.append(slot)

    mod.character_keys = keys
    mod.character_names = names
    mod.character_groups = groups
    mod.character_slots = slots
    return mod

# Scan fighter folder
def scan_fighter(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "fighter")
    
    if is_valid_dir(root_dir) == False:
        return mod
    
    mod = scan_character(root_dir, get_children(root_dir), mod)

    if search_dir_by_keyword(root_dir, "model"):
        mod.contains_skin = True
        mod.includes.append(SKIN)

    if search_dir_by_keyword(root_dir, "motion"):
        mod.contains_motion = True
        mod.includes.append(MOTION)

    if "kirby" in mod.display_name == False and search_dir_by_keyword(root_dir, "kirby"):
        mod.contains_kirby = True
        mod.includes.append(KIRBY_HAT)       

    return mod

def scan_effect(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "effect")

    if is_valid_dir(root_dir) == False:
        return mod

    if len(mod.character_names) <= 0:
        mod = scan_character(root_dir, get_children(os.path.join(root_dir, "fighter")), mod, False)

    for file in get_children_by_extension(root_dir, ".eff"):
        if search_files_for_pattern(file, r"c\d+"):
            mod.contains_one_slot_effect = True
            mod.includes.append(ONE_SLOT_EFFECT)
        else:
            mod.contains_effect = True
            mod.includes.append(ALL_SLOT_EFFECT)
        break
    
    if ALL_SLOT_EFFECT not in mod.includes and ONE_SLOT_EFFECT not in mod.includes:
        mod.contains_effect = True
        mod.includes.append(ALL_SLOT_EFFECT)    

    return mod

def scan_stage(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "stage")

    if is_valid_dir(root_dir):  
        mod.contains_stage = True
        mod.includes.append(STAGE)
    
    return mod

def scan_item(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "item")

    if is_valid_dir(root_dir):  
        mod.contains_item = True
        mod.includes.append(ITEM)

    return mod

def scan_sound(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "sound")

    if is_valid_dir(root_dir):  
        if search_dir_by_keyword(root_dir, "fighter_voice"):
            mod.contains_voice = True
            mod.includes.append(VOICE)

        if search_dir_by_keyword(root_dir, "fighter"):
            mod.contains_sfx = True
            mod.includes.append(SOUND)
        
        if search_dir_by_keyword(root_dir, "narration"):
            mod.contains_narrator = True
            mod.includes.append(NARRATOR)

    return mod

def scan_stream(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "stream")

    if is_valid_dir(root_dir):  
        mod.contains_victory_theme = True
        mod.includes.append(VICTORY_THEME)

    return mod

def scan_camera(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "camera")

    if is_valid_dir(root_dir):  
        mod.contains_victory_animation = True
        mod.includes.append(VICTORY_ANIMATION)
        
    return mod

def scan_ui(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "ui")

    if is_valid_dir(root_dir):  
        if search_dir_by_keyword(root_dir, "message"):
            message_dir = os.path.join(root_dir, "message")
            custom_name = get_children_by_extension(message_dir, ".msbt")
            single_name = get_children_by_extension(message_dir, ".xmsbt")

            if len(custom_name) > 0:
                mod.contains_name = True
                mod.includes.append(ALL_SLOT_NAME)
            elif len(single_name) > 0:
                mod.contains_one_slot_name = True
                mod.includes.append(ONE_SLOT_NAME)
            
        if search_dir_by_keyword(root_dir, "replace") or search_dir_by_keyword(root_dir, "replace_patch"):
            mod.contains_ui = True
            mod.includes.append(UI)
        
    return mod

def scan_thumbnail(mod:Mod)->Mod:
    img_path = os.path.join(mod.path, "preview.webp")
    if is_valid_file(img_path):
        mod.contains_thumbnail = True
        mod.thumbnail = img_path
    
    return mod

def scan_mod(mod:Mod)->Mod:
    """
    Scans mod directory and auto-fills information
    """
    def get_category(mod:Mod)->str:
        if mod.contains_skin or mod.contains_motion:
            return CATEGORY_FIGHTER
        elif mod.contains_stage:
            return CATEGORY_STAGE
        elif mod.contains_effect or mod.contains_one_slot_effect:
            return CATEGORY_EFFECTS
        elif mod.contains_voice or mod.contains_sfx or mod.contains_narrator:
            return CATEGORY_AUDIO
        elif mod.contains_ui:
            return CATEGORY_UI
        elif mod.contains_script:
            return CATEGORY_PARAM
        else:
            return CATEGORY_MISC

    mod.includes = []
    mod = scan_fighter(mod)
    mod = scan_effect(mod)
    mod = scan_stage(mod)
    mod = scan_item(mod)
    mod = scan_sound(mod)
    mod = scan_stream(mod)
    mod = scan_camera(mod)
    mod = scan_ui(mod)
    mod = scan_thumbnail(mod)
    mod.category = get_category(mod)
    mod.character = format_character_names(mod.character_names)
    mod.characters_grouped = group_char_name(mod.character_names, mod.character_groups)
    mod.character_slots_grouped = format_slots(mod.character_slots)

    if not mod.mod_name:
        mod.mod_name = get_mod_name(
            mod.display_name,
            mod.character_keys,
            mod.character_slots,
            mod.category
        )

    return mod
