"""
hash.py: contains methods for generating hash
"""

import zlib

MOD_DIRECTORY = "sd:/ultimate/mods/{0}"

def hash40(text:str):
    """
    Generates hash40 in hexidecimal format
    """
    encoded_hash = hex((len(text) << 32) + zlib.crc32(text.encode()))
    return encoded_hash

def get_hash(folder_name:str):
    """
    Generates hash encoding for the given mod directory
    Hash encoding is converted to decimal numbers
    This method replicates how ARCropolis generates hash for each mods in its workspace cache
    """
    mod_dir = MOD_DIRECTORY.format(folder_name)
    decimal = int(hash40(mod_dir), base=16)
    return decimal
