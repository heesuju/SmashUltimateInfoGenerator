class Mod:
    def __init__(self, **kwargs):
        # Default values
        self.display_name = ""
        self.description = ""
        self.authors = ""
        self.category = ""
        self.version = ""
        self.mod_name = ""
        self.url = ""
        self.wifi_safe = ""
        self.folder_name = ""
        self.path = ""
        self.character_slots = []
        self.stage_slots = []
        self.character_names = []
        self.character_groups = []
        self.character_keys = []
        self.includes = []
        
        self.thumbnail = ""
        self.hash = ""

        self.contains_info = False
        self.contains_skin = False
        self.contains_motion = False
        self.contains_script = False
        self.contains_kirby = False
        self.contains_stage = False
        self.contains_effect = False
        self.contains_one_slot_effect = False
        self.contains_item = False
        self.contains_voice = False
        self.contains_sfx = False
        self.contains_narrator = False
        self.contains_victory_theme = False
        self.contains_victory_animation = False
        self.contains_name = False
        self.contains_one_slot_name = False
        self.contains_ui = False
        self.contains_thumbnail = False

        self.is_selected = False
        self.update(**kwargs)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)