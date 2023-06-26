
from dotenv import dotenv_values, load_dotenv, find_dotenv
from typing import Any

class ConfigManager:
    """ConfigManager is a class that manages the config values
    """
    config: dict

    def __init__(self):
        file_path: str = find_dotenv(raise_error_if_not_found=True)
        load_dotenv(file_path)
        self.config = dotenv_values(file_path)

    def get(self, key: str) -> Any:
        """Get config value by key
        """
        return self.config[key]

    def get_or_default(self, key: str, default: Any) -> Any:
        """Get config value by key or return default value
        """
        return self.config.get(key, default)
