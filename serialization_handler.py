# serialization_handler.py
import json
import os
from datetime import datetime
from typing import Dict

class SerializationHandler:
    """Handles JSON serialization/deserialization for the application"""
    
    DATA_DIRECTORY = "data"

    @staticmethod
    def ensure_data_directory():
        """Ensure the data directory exists"""
        if not os.path.exists(SerializationHandler.DATA_DIRECTORY):
            os.makedirs(SerializationHandler.DATA_DIRECTORY)

    @staticmethod
    def get_file_path(filename: str) -> str:
        """Get the full file path in the data directory"""
        SerializationHandler.ensure_data_directory()
        if not filename.endswith('.json'):
            filename += '.json'
        return os.path.join(SerializationHandler.DATA_DIRECTORY, filename)

    @staticmethod
    def save_to_json(data: Dict, filename: str) -> bool:
        """Save data to a JSON file"""
        try:
            file_path = SerializationHandler.get_file_path(filename)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
            return False

    @staticmethod
    def load_from_json(filename: str) -> Dict:
        """Load data from a JSON file"""
        try:
            file_path = SerializationHandler.get_file_path(filename)
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading from JSON: {str(e)}")
            return {}