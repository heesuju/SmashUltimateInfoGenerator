"""
string_helper.py: Module containing methods to process strings
"""

import re

BLACKLIST_CHARS = [
    "<",
    ">",
    "?",
    "\"",
    ":",
    "|",
    "\\",
    "/",
    "*",
    ".",
    "’"]

SPECIAL_CHARS = [
    "[",
    "]",
    "_",
    ",",
    "!",
    "&",
    "#",
    "^"
] + BLACKLIST_CHARS

def clean_vesion(version:str)->str:
    """
    Returns formatted version(e.g. v1.0 -> 1.0.0)
    """
    parts = version.split('.')
    numeric_parts = [str(int(''.join(filter(str.isdigit, part)))) for part in parts]

    while len(numeric_parts) < 3:
        numeric_parts.append('0')

    formatted_version = '.'.join(numeric_parts)
    return formatted_version

def trim_consecutive(text:str, chars_to_remove:list[str])->str:
    """
    Removes consecutive characters if it is in the provided list
    Args:
        chars_to_remove (list): The list of text to check for consecutive occurrences
    """
    pattern = f"[{''.join(re.escape(c) for c in chars_to_remove)}]+"
    cleaned_text = re.sub(pattern, lambda m: m.group(0)[0], text)
    return cleaned_text

def remove_texts(text:str, text_to_remove:list):
    """
    Removes characters if it is in the provided list
    Args:
        text_to_remove (list): The list of text to remove
    """
    if len(text_to_remove) > 0:
        pattern = r'\b(?:' + '|'.join(re.escape(name) for name in text_to_remove) + r')(?=\s|_)'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    return text

def remove_special_chars(text:str)->str:
    """
    Removes certain special characters from string
    """
    for b in SPECIAL_CHARS:
        text = text.replace(b, " ")
    return text

def remove_paranthesis(text:str):
    """
    Removes any paranthesis or brackets that prefix the string
    """
    if text:
        text = remove_redundant_spacing(text)
        starts_with = ["(", "{", "-", "_", "~"]
        while text[0] in starts_with:
            if text[0] == "(":
                text = text.removeprefix("(")
                text = text.replace(")", "", 1)
            if text[0] == "{":
                text = text.removeprefix("{")
                text = text.replace("}", "", 1)
            if text[0] == "-":
                text = text.removeprefix("-")
            if text[0] == "_":
                text = text.removeprefix("_")
            if text[0] == "~":
                text = text.removeprefix("~")
            text = remove_redundant_spacing(text)
            text = text.removeprefix(" ")
            text = text.removesuffix(" ")
    return text

def add_spaces_to_camel_case(input_string:str)->str:
    """
    Adds spaces between camel case
    """
    if not input_string:
        return input_string

    result = [input_string[0]]

    for i in range(1, len(input_string)):
        char = input_string[i]
        prev_char = input_string[i - 1]

        if char.isupper() and prev_char.islower():
            result.append(' ')
        result.append(char)

    return ''.join(result)

def remove_non_eng(text:str)->str:
    """
    Removes non-English characters from the string
    """
    cleaned_text = re.sub(r'[^a-zA-Z]', ' ', text)
    cleaned_text = remove_redundant_spacing(cleaned_text)
    return cleaned_text

def is_digit(text:str, num_digits:int=3)->bool:
    """
    Returns whether the text is a number that has digits less than or equal to the provided limit
    """
    if (str.isdigit(text) and len(text) <= num_digits) or text == "":
        return True
    else:
        return False

def remove_redundant_spacing(text:str)->str:
    """
    Removes consecutive spaces from the string
    """
    parts = [i for i in text.split(' ') if i]
    return " ".join(parts)

def str_to_int(s:str, start_index:int = 0)->int:
    """
    Converts string to number if it is a digit
    If not, 0 will be returned
    """
    text = str(s[start_index:])
    num = 0
    if text.isdigit():
        num = int(text)

    return num
