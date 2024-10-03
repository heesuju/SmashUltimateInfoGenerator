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
    return mod_name

def extract_mod_name(display_name:str, characters:list, slots:list, category:str)->str:# remove consecutive commas!
    name = remove_text(display_name, characters + [category])
    name = remove_special_chars(name)
    name = remove_numbers(name, slots)
    name = clean_mod_name(name)
    name = remove_paranthesis(name)
    return name

def remove_text(text:str, texts_to_remove:list):
    arr_to_remove = []
    arr_to_remove = [remove_special_chars(t).replace(" ", "") for t in texts_to_remove]
    for t in texts_to_remove:
        cleaned_t = remove_special_chars(t)
        if cleaned_t not in arr_to_remove:
            arr_to_remove.append(cleaned_t)
    pattern = r'\b(?:' + '|'.join(re.escape(name) for name in arr_to_remove) + r')[^\s_]*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    return text

def remove_special_chars(text:str):
    to_remove = FOLDER_NAME_BLACKLIST + ["[", "]", "_", ",", "!", "?"]
    for b in to_remove:
        text = text.replace(b, " ")
    return text

def remove_numbers(text:str, numbers:list):
    pattern = r'\b[Cc]?0*(' + '|'.join(map(str, numbers)) + r')\b'
    cleaned_string = re.sub(pattern, '', text).strip()
    return cleaned_string

def remove_paranthesis(text:str):
    text = remove_redundant_spacing(text)
    if text[0] == "(":
        text = text.removeprefix("(")
        text = text.replace(")", "", 1)
    return text

def substitute_characters(text:str, chars_to_substitute:list)->str:
    chars_set = set(chars_to_substitute)
    result = ''.join([char if char not in chars_set else ' ' for char in text])
    return result