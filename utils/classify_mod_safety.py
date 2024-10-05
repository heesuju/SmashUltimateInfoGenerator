import re

# Example text scraped from the web
text = """
This mod is wifi-safe and tested for multiplayer use. However, it may cause desyncs in some online matches.
Do not use it in ranked games, as it might get you banned.
"""

# Define positive keywords/phrases
POSITIVE_PATTERNS = [
    r"wifi[-\s]?safe", 
    r"wi-fi[-\s]?safe", 
    r"safe\sfor\swifi", 
    r"compatible\swith\sonline\splay",
    r"tested\sfor\smultiplayer",
    r"works\swell\sover\sWiFi"
]

# Define negative keywords/phrases (indicating unsafe behavior)
NEGATIVE_PATTERNS = [
    r"not\s+wifi[-\s]?safe", 
    r"may\scause\sdesyncs", 
    r"not\srecommended\sfor\smultiplayer", 
    r"can\sget\syou\sbanned", 
    r"incompatible\swith\sonline",
    r"do\snot\suse\sonline",
    r"unsafe\sfor\sonline\splay"
]

# Define negations (e.g., "not" or "do not") near "wifi-safe"
NEGATION_PATTERNS = [
    r"(not|do\snot)\s+\w+\s+wifi[-\s]?safe",
    r"(not|do\snot)\s+recommend\sonline\suse",
    r"(not|do\snot)\s+work\sover\sWiFi"
]

# Function to check for positive patterns
def find_positive_patterns(text):
    for pattern in POSITIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Function to check for negative patterns
def find_negative_patterns(text):
    for pattern in NEGATIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Function to check for negations near "wifi-safe"
def find_negations(text):
    for pattern in NEGATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Rule-based classification
def classify_mod_safety(text)->str:
    score = 0
    
    if find_positive_patterns(text):
        score += 1
    
    if find_negative_patterns(text):
        score -= 1
    
    if find_negations(text):
        score -= 1

    if score > 0:
        return "Safe"
    elif score < 0:
        return "Not Safe"
    else:
        return "Uncertain"