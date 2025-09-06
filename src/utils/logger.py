import os
from datetime import datetime as dt
from data.cache import LOG_PATH

def output_log(*args)->None:
    messages = [arg for arg in args if isinstance(arg, str)]
    if len(messages) <= 0:
        return
    message = "\n".join(messages)

    file_name = dt.now().strftime("%Y%m%d_log.txt")
    path = os.path.join(LOG_PATH, file_name)
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    
    parts = message.split("\n")
    timestamp = dt.now().strftime("%H:%M:%S")
    for idx, part in enumerate(parts):
        if idx == 0:
            parts[0] = f"[{timestamp}] " + parts[0]
        else:
            parts[idx] = " " * 11 + parts[idx]

    output = "\n".join(parts) + "\n"
    with open(path, mode="a", encoding="utf-8") as o:
        o.write(output)
    print(output)