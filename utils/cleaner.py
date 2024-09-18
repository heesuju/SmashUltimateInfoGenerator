# returns formatted version(e.g. v1.0 -> 1.0.0) 
def format_version(input_str)->str:
    segments = input_str.split('.')
    numeric_parts = [str(int(''.join(filter(str.isdigit, part)))) for part in segments]
    while len(numeric_parts) < 3:
        numeric_parts.append('0')

    formatted_version = '.'.join(numeric_parts)
    return formatted_version