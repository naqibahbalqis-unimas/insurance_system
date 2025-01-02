# data_storage.py

import json

import os

from dataclasses import asdict

from datetime import datetime

from typing import Dict, Any

from policy_enums import PolicyType



class DataStorage:

    def __init__(self, storage_dir: str = "data"):

        """Initialize data storage with a directory for storing files"""

        self.storage_dir = storage_dir

        self._ensure_storage_exists()



    def _ensure_storage_exists(self):

        """Create storage directory if it doesn't exist"""

        if not os.path.exists(self.storage_dir):

            os.makedirs(self.storage_dir)



    def _serialize_datetime(self, obj: Any) -> Any:

        """Handle datetime serialization for JSON"""

        if isinstance(obj, datetime):

            return obj.isoformat()

        return obj



    def save_data(self, filename: str, data: Dict) -> bool:

        """Save data to a JSON file"""

        try:

            file_path = os.path.join(self.storage_dir, f"{filename}.json")

            # print(f"Saving data to: {file_path}")  # Debug print

            # print(f"Data being saved: {data}")     # Debug print

            with open(file_path, 'w') as f:

                json.dump(data, f, default=self._serialize_datetime, indent=4)

            return True

        except Exception as e:

            print(f"Error saving data: {str(e)}")

            return False



    def load_data(self, filename: str) -> Dict:

        """Load data from a JSON file"""

        try:

            file_path = os.path.join(self.storage_dir, f"{filename}.json")

            if os.path.exists(file_path):

                with open(file_path, 'r') as f:

                    return json.load(f)

            return {}

        except Exception as e:

            print(f"Error loading data: {str(e)}")

            return {}