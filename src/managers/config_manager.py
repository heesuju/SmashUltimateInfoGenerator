import json
from data.cache import PATH_CONFIG
from src.utils.file import is_valid_path, is_valid_file
from src.models.settings import Settings
from src.utils.logger import output_log

class ConfigManager():
    def __init__(self):
        self.config = None
        self.load()

    def load(self)->None:
        if(is_valid_file(PATH_CONFIG)):
            try:
                json_file = open(PATH_CONFIG, "r", encoding="utf-8")
                data = json.loads(json_file.read())
                settings = Settings(**data)
                json_file.close()
                output_log("Loaded config")
                self.config = settings
                
                # Set default format templates if empty
                if not self.config.name_rules.folder_name_format:
                    self.config.name_rules.folder_name_format = "{category}_{characters}[{slots}]_{mod}"
                if not self.config.name_rules.display_name_format:
                    self.config.name_rules.display_name_format = "{characters} {slots} {mod}"
                
                # Save config with defaults if they were added
                self.save()
                return None
            except Exception as e:
                output_log(f"Failed to load config: {e}")
        
        output_log(f"No config found\nMaking new config...")
        self.config = Settings()
        
        # Set default format templates for new config
        self.config.name_rules.folder_name_format = "{category}_{characters}{slots}_{mod}"
        self.config.name_rules.display_name_format = "{characters} {slots} {mod}"
        
        self.save()
    
    def save(self)->None:
        try:
            with open(PATH_CONFIG, 'w', encoding='utf-8') as f:
                f.write(self.config.model_dump_json(indent=4))
                output_log(f"Saved config")
        except Exception as e:
            output_log(f"Failed to save config: {e}")