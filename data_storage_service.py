# data_storage_service.py
import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
from policy_enums import PolicyType

class DataStorageService:
    DATA_DIR = "data"
    DATA_FILE = os.path.join(DATA_DIR, "customer_data.json")

    @staticmethod
    def _serialize_datetime(obj: Any) -> Any:
        """Handle datetime serialization for JSON"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    @staticmethod
    def _ensure_storage_exists():
        """Create storage directory if it doesn't exist"""
        os.makedirs(DataStorageService.DATA_DIR, exist_ok=True)

    @staticmethod
    def load_data() -> Dict:
        """Load all data from the JSON file."""
        try:
            DataStorageService._ensure_storage_exists()
            if os.path.exists(DataStorageService.DATA_FILE):
                with open(DataStorageService.DATA_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return {}

    @staticmethod
    def save_data(data: Dict) -> bool:
        """Save data to the JSON file."""
        try:
            DataStorageService._ensure_storage_exists()
            with open(DataStorageService.DATA_FILE, 'w') as f:
                json.dump(data, f, default=DataStorageService._serialize_datetime, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False

    @staticmethod
    def clean_customer_data(data: Dict) -> Dict:
        """Clean up and restructure customer data if needed."""
        try:
            cleaned_data = {}
            for email, customer_data in data.items():
                if isinstance(customer_data, dict) and "customer_info" in customer_data:
                    cleaned_data[email] = {
                        "customer_info": customer_data["customer_info"],
                        "policies": {}
                    }
                    # Merge policies from all possible locations
                    if "policies" in customer_data:
                        cleaned_data[email]["policies"].update(customer_data["policies"])

            return cleaned_data
        except Exception as e:
            print(f"Error cleaning data: {str(e)}")
            return data

    @staticmethod
    def save_customer_data(customer: Any) -> bool:
        """Save customer data while preserving existing data."""
        try:
            # Load and clean existing data
            existing_data = DataStorageService.load_data()
            cleaned_data = DataStorageService.clean_customer_data(existing_data)
            
            # Create new customer data
            customer_data = {
                "customer_info": {
                    "email": customer.email,
                    "name": customer.name,
                    "contact_number": customer._contact_number,
                    "address": customer.address,
                    "birth_date": customer.birth_date.strftime("%Y-%m-%d"),
                    "credit_score": customer.credit_score
                },
                "policies": {}
            }

            # If customer exists, preserve existing policies
            if customer.email in cleaned_data:
                customer_data["policies"] = cleaned_data[customer.email]["policies"]

            # Update with new policies
            for policy in customer.policies:
                policy_id = policy.get_policy_id()
                policy_dict = policy.to_dict()
                # Ensure status is converted to string if it's an enum
                if 'status' in policy_dict:
                    policy_dict['status'] = str(policy_dict['status'])
                customer_data["policies"][policy_id] = policy_dict

            # Update the data
            cleaned_data[customer.email] = customer_data

            # Save to file
            if DataStorageService.save_data(cleaned_data):
                print(f"Data saved successfully to {DataStorageService.DATA_FILE}")
                return True
            return False
        except Exception as e:
            print(f"Error saving customer data: {str(e)}")
            return False

    @staticmethod
    def load_customer_data(email: str) -> Optional[Dict]:
        """Load customer data for a specific email."""
        try:
            data = DataStorageService.load_data()
            cleaned_data = DataStorageService.clean_customer_data(data)
            if email in cleaned_data:
                print(f"Found data for {email}")
                return cleaned_data[email]
            print(f"No data found for {email}")
            return None
        except Exception as e:
            print(f"Error loading customer data: {str(e)}")
            return None

    @staticmethod
    def get_highest_policy_number() -> int:
        """Get the highest policy number from all existing policies."""
        try:
            data = DataStorageService.load_data()
            highest_num = 0
            
            for customer_data in data.values():
                policies = customer_data.get("policies", {})
                for policy_id in policies.keys():
                    try:
                        num = int(policy_id[3:])
                        highest_num = max(highest_num, num)
                    except (ValueError, IndexError):
                        continue
                        
            return highest_num
        except Exception as e:
            print(f"Error getting highest policy number: {str(e)}")
            return 0