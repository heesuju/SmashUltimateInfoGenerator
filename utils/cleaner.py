import re

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
    print(mod_name)

def substitute_characters(text:str, chars_to_substitute:list)->str:
    chars_set = set(chars_to_substitute)
    result = ''.join([char if char not in chars_set else ' ' for char in text])
    return result