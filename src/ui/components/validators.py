
def limit_version(text:str):
    result = ""
    for c in text:
        if c.isdigit():
            result += c
        elif c == ".":
            if not result or result[-1] == ".":
                continue  # skip consecutive dot
            result += "."
    return result[:10]