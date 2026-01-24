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
from src.models.mod import Mod, Character
from src.constants.enums import Category, Element, Fighter
from .formatting import (
    format_slots,
    get_mod_name,
    format_character_names,
    group_char_name
)

from src.managers.data_manager import DataManager

def scan_character(mod:Mod)->Mod:
    def get_slots_as_number(slots:list[str])->list[int]:
        numbers = []
        for s in slots:
            match = re.search(r'\d+', s)
            if match:
                numbers.append(int(match.group()))

        numbers.sort()
        return numbers
    
    fighter_dir = os.path.join(mod.path, "fighter")
    effect_dir = os.path.join(mod.path, "effect", "fighter")
    skin_fighters = get_children(fighter_dir)
    eff_fighters = get_children(effect_dir)

    if len(skin_fighters) > 1 and "kirby" in skin_fighters:
        skin_fighters.remove("kirby")

    names = list(set(skin_fighters + eff_fighters))
    
    for name in names:
        fighter = Fighter(name)
        character = Character(fighter=fighter, slots=[])

        if name in skin_fighters:
            path = os.path.join(fighter_dir, name)
            model_dir = os.path.join(path, "model")
            if is_valid_dir(model_dir):
                models = get_children(model_dir)
                found_model = False
                for model in models:
                    slot_strings = get_children(os.path.join(model_dir, model))
                    # Scan inside c0X files
                    if found_model == False and len(slot_strings) > 0:
                        model_files = get_direct_child_by_extension(os.path.join(model_dir, model, slot_strings[0]))
                        found_model = False
                        for model_file in model_files:
                            tmp_arr = model_file.split(".")
                            if "model" in tmp_arr:
                                found_model = True
                                break

                    # Get a list of model slots
                    slots = get_slots_as_number(slot_strings)
                    for slot in slots:
                        if slot not in character.slots:
                            character.slots.append(slot)   
                if found_model == False:
                    mod.add_to_included(Element.RECOLOR)

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
        if Element.RECOLOR not in mod.includes:
            mod.add_to_included(Element.SKIN)

    if search_dir_by_keyword(root_dir, "motion"):
        mod.add_to_included(Element.MOTION)

    if "kirby" in mod.display_name == False and search_dir_by_keyword(root_dir, "kirby"):
        mod.add_to_included(Element.KIRBY_HAT)       

    return mod

def scan_effect(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "effect")

    if is_valid_dir(root_dir) == False:
        return mod

    for file in get_children_by_extension(root_dir, ".eff"):
        if search_files_for_pattern(file, r"c\d+"):
            mod.add_to_included(Element.ONE_EFFECT)
        else:
            mod.add_to_included(Element.ALL_EFFECT)
        break
    
    if Element.ALL_EFFECT not in mod.includes and Element.ONE_EFFECT not in mod.includes:
        mod.add_to_included(Element.ALL_EFFECT)    

    return mod

def scan_stage(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "stage")

    if is_valid_dir(root_dir):  
        mod.add_to_included(Element.STAGE)
    
    return mod

def scan_item(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "item")

    if is_valid_dir(root_dir):  
        mod.add_to_included(Element.ITEM)

    return mod

def scan_sound(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "sound")

    if is_valid_dir(root_dir):  
        if search_dir_by_keyword(root_dir, "fighter_voice"):
            mod.add_to_included(Element.VOICE)

        if search_dir_by_keyword(root_dir, "fighter"):
            mod.add_to_included(Element.SOUND)
        
        if search_dir_by_keyword(root_dir, "narration"):
            mod.add_to_included(Element.NARRATOR)

    return mod

def scan_stream(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "stream")

    if is_valid_dir(root_dir):  
        mod.add_to_included(Element.V_THEME)

    return mod

def scan_camera(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "camera")

    if is_valid_dir(root_dir):
        mod.add_to_included(Element.V_ANIMATION)
        
    return mod

def scan_ui(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "ui")

    if is_valid_dir(root_dir):  
        if search_dir_by_keyword(root_dir, "message"):
            message_dir = os.path.join(root_dir, "message")
            custom_name = get_children_by_extension(message_dir, ".msbt")
            single_name = get_children_by_extension(message_dir, ".xmsbt")

            if len(custom_name) > 0:
                mod.add_to_included(Element.ALL_NAME)
            elif len(single_name) > 0:
                mod.add_to_included(Element.ONE_NAME)
            
        if search_dir_by_keyword(root_dir, "replace") or search_dir_by_keyword(root_dir, "replace_patch"):
            mod.add_to_included(Element.UI)
        
    return mod

def scan_thumbnail(mod:Mod)->Mod:
    img_path = os.path.join(mod.path, "preview.webp")
    if is_valid_file(img_path):
        mod.thumbnail = img_path
    
    return mod

def scan_flags(mod:Mod)->Mod:
    root_dir = os.path.join(mod.path, "flags")

    if is_valid_dir(root_dir):
        mod.add_to_included(Element.FLAGS)
    
    return mod

def scan_plugin(mod:Mod)->Mod:
    plugin_path = os.path.join(mod.path, "plugin.nro")

    if is_valid_file(plugin_path):
        mod.add_to_included(Element.PLUGIN)
    
    return mod

def scan_mod(mod:Mod)->Mod:
    """
    Scans mod directory and auto-fills information
    """
    def get_category(mod:Mod)->str:
        if Element.SKIN in mod.includes or Element.MOTION in mod.includes or Element.RECOLOR in mod.includes:
            return Category.FIGHTER
        elif Element.STAGE in mod.includes:
            return Category.STAGE
        elif Element.ONE_EFFECT in mod.includes or Element.ALL_EFFECT in mod.includes:
            return Category.EFFECTS
        elif Element.VOICE in mod.includes or Element.SOUND in mod.includes or Element.NARRATOR in mod.includes:
            return Category.AUDIO
        elif Element.UI in mod.includes:
            return Category.UI
        elif Element.FLAGS in mod.includes:
            return Category.PARAM
        elif len(mod.characters) > 0:
            return Category.FIGHTER
        else:
            return Category.MISC
        
    def check_includes(includes:list[str])->list[str]:
        output_arr = includes
        if Element.SKIN in output_arr and Element.RECOLOR in output_arr:
            output_arr.remove(Element.SKIN)
        if Element.ALL_EFFECT in output_arr and Element.ONE_EFFECT in output_arr:
            output_arr.remove(Element.ONE_EFFECT)
        if Element.ALL_NAME in output_arr and Element.ONE_NAME in output_arr:
            output_arr.remove(Element.ONE_NAME)
        return output_arr
    
    mod.characters = []
    mod = scan_character(mod)
    mod = scan_fighter(mod)
    mod = scan_effect(mod)
    mod = scan_stage(mod)
    mod = scan_item(mod)
    mod = scan_sound(mod)
    mod = scan_stream(mod)
    mod = scan_camera(mod)
    mod = scan_ui(mod)
    mod = scan_thumbnail(mod)
    mod = scan_flags(mod)
    mod = scan_plugin(mod)
    
    mod.category = get_category(mod)
    
    mod.includes = check_includes(mod.includes)

    keys = mod.get_character_keys()
    slots = mod.get_character_slots()

    if not mod.mod_name:
        mod.mod_name = get_mod_name(
            mod.display_name,
            keys,
            slots,
            str(mod.category)
        )

    return mod
