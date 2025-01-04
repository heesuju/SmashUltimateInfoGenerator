import os
from datetime import datetime as dt
from src.config.defs import LOG_DIR

def output_log(message:str):
    file_name = dt.now().strftime("%Y%m%d_log.txt")
    path = os.path.join(LOG_DIR, file_name)
    output = "[{0}] {1}\n".format(dt.now().strftime("%H:%M:%S"), message)
    with open(path, mode="a", encoding="utf-8") as o:
        o.write(output)
    print(output)