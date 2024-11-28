import json
import os
from dataclasses import dataclass
from typing import TextIO


@dataclass
class DatabaseConfig:
    DB_URL: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DBNAME: str


@dataclass
class DiscordConfig:
    SUPER_SECRET_TOKEN: str


class ConfigLoader:
    def __init__(self, config_path="config/sys_config.json"):
        self.config_path = config_path
        self.database = None
        self.discord = None

        # Load the configuration
        self.load_config()

    def load_config(self):
        """
        Load configuration values from a JSON file. If the file is not found,
        create a new file with a default structure and load it.
        """
        # Default configuration structure
        default_config = {
            "Database": {
                "DB_URL": "localhost",
                "DB_PORT": 5234,
                "DB_USER": "discord_bot",
                "DB_PASSWORD": "your_password_here",
                "DB_DBNAME": "discord_dnd"
            },
            "Discord": {
                "SUPER_SECRET_TOKEN": "your_discord_token_here"
            }
        }

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        # Check if the file exists
        if not os.path.exists(self.config_path):
            # Create the file with the default structure
            with open(self.config_path, "w") as config_file:
                json.dump(default_config, config_file, indent=4)
            print(f"Config file not found. A new file has been created at: {self.config_path}")

        # Load the file
        with open(self.config_path, "r") as config_file:
            try:
                config_data = json.load(config_file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing JSON config file: {e}")

        # Map the loaded data to data objects
        self._map_to_objects(config_data)

    def _map_to_objects(self, config_data):
        """
        Map the JSON configuration data to data objects.

        Args:
            config_data (dict): Parsed configuration data.
        """
        self.database = DatabaseConfig(**config_data["Database"])
        self.discord = DiscordConfig(**config_data["Discord"])

    def save_config(self):
        """
        Save the current configuration back to the JSON file.
        """
        config_data = {
            "Database": vars(self.database),
            "Discord": vars(self.discord)
        }
        with open(self.config_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)
        print(f"Configuration saved to: {self.config_path}")
