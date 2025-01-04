import zlib

MOD_DIRECTORY = "sd:/ultimate/mods/{0}"

def hash40(str):
    hash40 = hex((len(str) << 32) + zlib.crc32(str.encode()))
    return hash40

def get_hash(folder_name):
    mod_dir = MOD_DIRECTORY.format(folder_name)
    decimal = int(hash40(mod_dir), base=16)
    return decimal