"""
toml.py: Contains various methods for reading and writing TOML file format
"""

import os
import tomli as t
import tomli_w as tw
from .common import is_valid_file

INFO_TOML = "info.toml"

def load_toml(directory:str) -> dict:
    """
    Loads a TOML file from the specified directory and returns the data as a dictionary

    Args:
        directory (str): The directory containing the TOML file
    """
    file_path = os.path.join(directory, INFO_TOML)
    if not is_valid_file(file_path):
        return None
    try:
        with open(file_path, "rb") as toml_file:
            return t.load(toml_file)
    except FileNotFoundError:
        print("File not found. Please check the directory and file name.")
    except PermissionError:
        print("Permission denied. Unable to access the file.")
    except OSError as e:
        print(f"File access error: {e}")

def dump_toml(directory:str, data:dict)->bool:
    """
    Writes a dict to a toml file
    Returns whether the process was successful or not

    Args:
        directory (str): The directory to write to
    """
    result = False
    output_path = os.path.join(directory, INFO_TOML)
    try:
        with open(output_path, "wb") as toml_file:
            tw.dump(data, toml_file)

        result = True
    except FileNotFoundError:
        print("File not found. Please check the directory and file name.")
    except PermissionError:
        print("Permission denied. Unable to access the file.")
    except OSError as e:
        print(f"File access error: {e}")

    return result
