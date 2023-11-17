class Mod:
    def __init__(self, folder_name, display_name, authors, category, version, characters, slots, mod_name, selected) -> None:
        self.folder_name = folder_name
        self.display_name = display_name
        self.authors = authors
        self.category = category
        self.version = version
        self.characters = characters
        self.slots = slots
        self.mod_name = mod_name
        self.selected = selected
        self.path = ""
        self.info_toml = False
        self.img = None