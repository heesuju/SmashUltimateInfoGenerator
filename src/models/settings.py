class Settings():
    def __init__(self, **kwargs):
        """
        Default values for settings
        """
        self.default_directory = ""
        self.is_slot_capped = True
        self.start_with_editor = False
        self.display_name_format = "{characters} {slots} {mod}"
        self.folder_name_format = "{category}_{characters}[{slots}]_{mod}"
        self.additional_elements = []
        self.sort_priority = [
            {"column": "category", "order": "Ascending"},
            {"column": "characters.custom", "order": "Ascending"},
            {"column": "characters.slots", "order": "Ascending"},
            {"column": "mod_name", "order": "Ascending"}
        ]
        self.cache_dir = ""
        self.workspace = "Default"
        self.close_on_apply = True
        self.update(**kwargs)

    def update(self, **kwargs):
        """
        Updates attribute values with dict
        Usage:
            settings = Settings(**dict)
            or
            settings = Settings()
            settings.update(**dict)
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)