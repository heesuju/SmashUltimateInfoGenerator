import os
import re
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
from src.models.character import Character
from src.constants.elements import *
from src.constants.categories import *
from .formatting import (
    format_slots,
    get_mod_name,
    format_character_names,
    group_char_name
)
from data import PATH_CHAR_NAMES

def get_character(code:str, character_data:dict)->dict:
    for data in character_data:
        if code == data['Key']:
            return data
    return None

def scan_character(mod:Mod)->Mod:
    def get_slots_as_number(slots:list[str])->list[int]:
        numbers = []
        for s in slots:
            match = re.search(r'\d+', s)
            if match:
                numbers.append(int(match.group()))

        numbers.sort()
        return numbers

    character_dict = csv_to_dict(PATH_CHAR_NAMES)
    fighter_dir = os.path.join(mod.path, "fighter")
    effect_dir = os.path.join(mod.path, "effect", "fighter")
    skin_fighters = get_children(fighter_dir)
    eff_fighters = get_children(effect_dir)

    if len(skin_fighters) > 1 and "kirby" in skin_fighters:
        skin_fighters.remove("kirby")

    names = list(set(skin_fighters + eff_fighters))
    
    for name in names:
        dict = get_character(name, character_dict)
        character = Character(**dict)

        if name in skin_fighters:
            path = os.path.join(fighter_dir, name)
            model_dir = os.path.join(path, "model")
            if is_valid_dir(model_dir):
                models = get_children(model_dir)

                for model in models:
                    slot_strings = get_children(os.path.join(model_dir, model))
                    slots = get_slots_as_number(slot_strings)
                    for slot in slots:
                        if slot not in character.slots:
                            character.slots.append(slot)   
        if name in eff_fighters:
            path = os.path.join(effect_dir, name)
            all_slots = get_direct_child_by_extension(path, ".eff")
        
            slots = get_slots_as_number(all_slots)
            for slot in slots:
                if slot not in character.slots:
                    character.slots.append(slot)
        
        mod.characters.append(character)

    return mod

# Scan fighter folder
def scan_fighter(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "fighter")
    
    if is_valid_dir(root_dir) == False:
        return mod

    if search_dir_by_keyword(root_dir, "model"):
        mod.add_to_included(SKIN)

    if search_dir_by_keyword(root_dir, "motion"):
        mod.add_to_included(MOTION)

    if "kirby" in mod.display_name == False and search_dir_by_keyword(root_dir, "kirby"):
        mod.add_to_included(KIRBY_HAT)       

    return mod

def scan_effect(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "effect")

    if is_valid_dir(root_dir) == False:
        return mod

    for file in get_children_by_extension(root_dir, ".eff"):
        if search_files_for_pattern(file, r"c\d+"):
            mod.add_to_included(ONE_SLOT_EFFECT)
        else:
            mod.add_to_included(ALL_SLOT_EFFECT)
        break
    
    if ALL_SLOT_EFFECT not in mod.includes and ONE_SLOT_EFFECT not in mod.includes:
        mod.add_to_included(ALL_SLOT_EFFECT)    

    return mod

def scan_stage(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "stage")

    if is_valid_dir(root_dir):  
        mod.add_to_included(STAGE)
    
    return mod

def scan_item(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "item")

    if is_valid_dir(root_dir):  
        mod.add_to_included(ITEM)

    return mod

def scan_sound(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "sound")

    if is_valid_dir(root_dir):  
        if search_dir_by_keyword(root_dir, "fighter_voice"):
            mod.add_to_included(VOICE)

        if search_dir_by_keyword(root_dir, "fighter"):
            mod.add_to_included(SOUND)
        
        if search_dir_by_keyword(root_dir, "narration"):
            mod.add_to_included(NARRATOR)

    return mod

def scan_stream(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "stream")

    if is_valid_dir(root_dir):  
        mod.add_to_included(VICTORY_THEME)

    return mod

def scan_camera(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "camera")

    if is_valid_dir(root_dir):
        mod.add_to_included(VICTORY_ANIMATION)
        
    return mod

def scan_ui(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "ui")

    if is_valid_dir(root_dir):  
        if search_dir_by_keyword(root_dir, "message"):
            message_dir = os.path.join(root_dir, "message")
            custom_name = get_children_by_extension(message_dir, ".msbt")
            single_name = get_children_by_extension(message_dir, ".xmsbt")

            if len(custom_name) > 0:
                mod.add_to_included(ALL_SLOT_NAME)
            elif len(single_name) > 0:
                mod.add_to_included(ONE_SLOT_NAME)
            
        if search_dir_by_keyword(root_dir, "replace") or search_dir_by_keyword(root_dir, "replace_patch"):
            mod.add_to_included(UI)
        
    return mod

def scan_thumbnail(mod:Mod)->Mod:
    img_path = os.path.join(mod.path, "preview.webp")
    if is_valid_file(img_path):
        mod.thumbnail = img_path
    
    return mod

def scan_mod(mod:Mod)->Mod:
    """
    Scans mod directory and auto-fills information
    """
    def get_category(mod:Mod)->str:
        if SKIN in mod.includes or MOTION in mod.includes:
            return CATEGORY_FIGHTER
        elif STAGE in mod.includes:
            return CATEGORY_STAGE
        elif ONE_SLOT_EFFECT in mod.includes or ALL_SLOT_EFFECT in mod.includes:
            return CATEGORY_EFFECTS
        elif VOICE in mod.includes or SOUND in mod.includes or NARRATOR in mod.includes:
            return CATEGORY_AUDIO
        elif UI in mod.includes:
            return CATEGORY_UI
        else:
            return CATEGORY_MISC

    mod.characters = []
    mod = scan_fighter(mod)
    mod = scan_effect(mod)
    mod = scan_character(mod)
    mod = scan_stage(mod)
    mod = scan_item(mod)
    mod = scan_sound(mod)
    mod = scan_stream(mod)
    mod = scan_camera(mod)
    mod = scan_ui(mod)
    mod = scan_thumbnail(mod)
    mod.category = get_category(mod)

    keys, names, groups, series, slots = mod.get_character_data()

    if not mod.mod_name:
        mod.mod_name = get_mod_name(
            mod.display_name,
            keys,
            slots,
            mod.category
        )

    return mod
