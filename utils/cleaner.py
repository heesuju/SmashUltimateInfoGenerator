import re
from common import csv2dict, PATH_CHAR_NAMES

FOLDER_NAME_BLACKLIST = ["<", ">", "?", "\"", ":", "|", "\\", "/", "*", ".", "’"]

# returns formatted version(e.g. v1.0 -> 1.0.0) 
def format_version(input_str)->str:
    segments = input_str.split('.')
    numeric_parts = [str(int(''.join(filter(str.isdigit, part)))) for part in segments]
    while len(numeric_parts) < 3:
        numeric_parts.append('0')

    formatted_version = '.'.join(numeric_parts)
    return formatted_version

def remove_redundant_spacing(input:str):
    arr = [i for i in input.split(' ') if i]
    return " ".join(arr)

def clean_mod_name(mod_name:str)->str:
    pattern = r"^(.*?)\s+over\s+"
    match = re.match(pattern, mod_name)
    if match:
        mod_name = match.group(1)
    mod_name = substitute_characters(mod_name, FOLDER_NAME_BLACKLIST)
    mod_name = remove_redundant_spacing(mod_name)
    return mod_name

def extract_mod_name(display_name:str, characters:list, slots:list, category:str)->str:
    name = remove_text(display_name, [category])
    name = remove_characters(name, characters)
    name = remove_special_chars(name)
    name = remove_numbers(name, slots)
    name = clean_mod_name(name)
    name = remove_paranthesis(name)
    name = add_spaces_to_camel_case(name)
    return name

def remove_text(text:str, texts_to_remove:list):
    if len(texts_to_remove) > 0:
        pattern = r'\b(?:' + '|'.join(re.escape(name) for name in texts_to_remove) + r')[^\s_]*'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    return text

def remove_special_chars(text:str):
    to_remove = FOLDER_NAME_BLACKLIST + ["[", "]", "_", ",", "!", "&", "#", "^"]
    for b in to_remove:
        text = text.replace(b, " ")
    return text

def remove_numbers(text:str, numbers:list):
    pattern = r'\b[Cc]?0*(' + '|'.join(map(str, numbers)) + r')\b'
    cleaned_string = re.sub(pattern, '', text).strip()
    return cleaned_string

def remove_paranthesis(text:str):
    text = remove_redundant_spacing(text)
    if text:
        if text[0] == "(":
            text = text.removeprefix("(")
            text = text.replace(")", "", 1)
    return text

def substitute_characters(text:str, chars_to_substitute:list)->str:
    chars_set = set(chars_to_substitute)
    result = ''.join([char if char not in chars_set else ' ' for char in text])
    return result

def add_spaces_to_camel_case(input_string:str):
    result = [input_string[0]]
    
    for i in range(1, len(input_string)):
        char = input_string[i]
        prev_char = input_string[i - 1]
        
        if char.isupper() and prev_char.islower():
            result.append(' ')
        result.append(char)
    
    return ''.join(result)

def remove_characters(text:str, characters:list):
    arr_to_remove = []
    set_char = set()
    char_dict = csv2dict(PATH_CHAR_NAMES)
    for ch in characters:
        set_char.add(ch)
        data = char_dict.get(ch, None)
        if data is None: 
            continue
        
        for v in data[:-1]:
            if v:
                set_char.add(v)
    
    list_char = list(set_char)
    for item in list_char:
        set_char.add(remove_special_chars(item))
        set_char.add(remove_special_chars(item).replace(" ", ""))
    arr_to_remove = list(set_char)
    text = remove_text(text, arr_to_remove)
    return text