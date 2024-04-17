import zlib

def make_hash40(str):
    hash40 = hex((len(str) << 32) + zlib.crc32(str.encode()))
    return hash40

def gen_hash_as_decimal(folder_name):
    mod_dir = "sd:/ultimate/mods/" + folder_name
    decimal = int(make_hash40(mod_dir), base=16)
    return decimal