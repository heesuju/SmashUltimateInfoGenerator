class Settings():
    def __init__(self, **kwargs):
        """
        Default values for settings
        """
        self.default_directory:str = ""
        self.is_slot_capped:bool = True
        self.start_with_editor:bool = False
        self.display_name_format:str = "{characters} {slots} {mod}"
        self.folder_name_format:str = "{category}_{characters}[{slots}]_{mod}"
        self.additional_elements:list[str] = []
        self.sort_priority:list[dict] = [
            {"column": "category", "order": "Ascending"},
            {"column": "characters.custom", "order": "Ascending"},
            {"column": "characters.slots", "order": "Ascending"},
            {"column": "mod_name", "order": "Ascending"}
        ]
        self.cache_dir:str = ""
        self.workspace:str = "Default"
        self.close_on_apply:bool = True
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