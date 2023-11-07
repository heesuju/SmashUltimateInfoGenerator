import zlib

def make_hash40(str):
    hash40 = hex((len(str) << 32) + zlib.crc32(str.encode()))
    return hash40

def gen_hash(folder_name):
    mod_dir = "sd:/ultimate/mods/" + folder_name
    return make_hash40(mod_dir)