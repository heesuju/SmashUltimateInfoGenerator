"""
edit_distance.py: contains methods to calculate edit distance
edit distance(aka levenshtein distance) is used to quantify the similarity between two texts
"""

def get_edit_distance(text1:str, text2:str)->float:
    """
    returns the edit distance between two strings
    The distance is normalized between 0.0 to 1.0 based on the length of the string
    """
    if len(text1) > len(text2):
        text1, text2 = text2, text1

    distances = range(len(text1) + 1)
    for idx2, char2 in enumerate(text2):
        distances_ = [idx2 + 1]
        for idx1, char1 in enumerate(text1):
            if char1 == char2:
                distances_.append(distances[idx1])
            else:
                distances_.append(1 + min((distances[idx1], distances[idx1 + 1], distances_[-1])))
        distances = distances_

    def normalize(a:str, b:str, distance:float)->float:
        max_len = max(len(a), len(b))
        return distance/max_len

    return normalize(text1, text2, distances[-1])

def get_completion(text:str, values:list)->None:
    """
    Calculates the edit distance for each of the values
    Returns the most similar match
    """
    def get_cleaned(text:str)->str:
        text = text.lower()
        text = text.replace(" ", "")
        text = text.replace(".", "")
        return text

    if not text:
        return ""
    elif text not in values:
        min_num = 20.0
        min_text = ""
        for cat in values:
            dist = get_edit_distance(get_cleaned(text), get_cleaned(cat))
            if dist == min_num:
                if get_cleaned(text) not in get_cleaned(min_text):
                    min_text = cat
            elif dist < min_num:
                min_num = dist
                min_text = cat
        return min_text
    else:
        return text
