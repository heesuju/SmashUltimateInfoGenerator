import json
from src.core.data import PATH_CONFIG
from src.utils.file import is_valid_path, is_valid_file
from src.models.settings import Settings
from src.utils.logger import output_log

class ConfigManager():
    def __init__(self):
        self.config = None
        self.load()

    def load(self)->None:
        config_loaded_successfully = False
        if(is_valid_file(PATH_CONFIG)):
            try:
                json_file = open(PATH_CONFIG, "r", encoding="utf-8")
                data = json.loads(json_file.read())
                if "favorites" in data and isinstance(data["favorites"], list):
                    data["favorites"] = [str(item) for item in data["favorites"]]

                if "hidden_folders" in data and isinstance(data["hidden_folders"], list):
                    data["hidden_folders"] = [str(item) for item in data["hidden_folders"]]
                    
                settings = Settings(**data)
                json_file.close()
                output_log("Loaded config")
                self.config = settings
                config_loaded_successfully = True
            except Exception as e:
                output_log(f"Failed to load config: {e}")
        
        if not config_loaded_successfully:
            # Backup corrupted config if it exists
            if is_valid_file(PATH_CONFIG):
                try:
                    import shutil
                    backup_path = PATH_CONFIG + ".bak"
                    shutil.copy2(PATH_CONFIG, backup_path)
                    output_log(f"Backed up corrupted config to {backup_path}")
                except Exception as e:
                    output_log(f"Failed to backup corrupted config: {e}")

            output_log(f"No config found or load failed\nMaking new config...")
            self.config = Settings()
        
        # Set default sort rules if empty
        if not self.config.sort_rules:
            from src.models.settings import SortRule
            self.config.sort_rules = [
                SortRule(name="Category", priority=1, asc=True),
                SortRule(name="Characters", priority=2, asc=True),
                SortRule(name="Mod Name", priority=3, asc=True),
                SortRule(name="Slots", priority=4, asc=True)
            ]
        
        # Set default format templates if empty
        if not self.config.name_rules.folder_name_format:
            self.config.name_rules.folder_name_format = "{category}_{characters}[{slots}]_{mod}"
        if not self.config.name_rules.display_name_format:
            self.config.name_rules.display_name_format = "{characters} {slots} {mod}"
        
        self.save()
    
    def save(self)->None:
        try:
            with open(PATH_CONFIG, 'w', encoding='utf-8') as f:
                f.write(self.config.model_dump_json(indent=4))
                output_log(f"Saved config")
        except Exception as e:
            output_log(f"Failed to save config: {e}")