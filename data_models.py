# data_storage_service.py
import json
import os
from datetime import datetime
from typing import Dict, Optional, Any

class DataStorageService:
    DATA_FILE = "data/customer_data.json"

    @staticmethod
    def ensure_data_directory():
        directory = os.path.dirname(DataStorageService.DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def load_data() -> Dict:
        """Load all data from the JSON file."""
        try:
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
            DataStorageService.ensure_data_directory()
            with open(DataStorageService.DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False

    @staticmethod
    def save_customer_data(customer: Any) -> bool:
        """Save customer data while preserving existing data."""
        try:
            # Load existing data
            existing_data = DataStorageService.load_data()
            
            # Get existing customer data if it exists
            existing_customer_data = existing_data.get(customer.email, {})
            existing_policies = existing_customer_data.get("policies", {})

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
                "policies": existing_policies  # Start with existing policies
            }

            # Update with new policies
            for policy in customer.policies:
                policy_id = policy.get_policy_id()
                customer_data["policies"][policy_id] = policy.to_dict()

            # Update the customer data in the existing data
            existing_data[customer.email] = customer_data

            # Save the updated data
            return DataStorageService.save_data(existing_data)
        except Exception as e:
            print(f"Error saving customer data: {str(e)}")
            return False

    @staticmethod
    def load_customer_data(email: str) -> Optional[Dict]:
        """Load customer data for a specific email."""
        try:
            data = DataStorageService.load_data()
            return data.get(email)
        except Exception as e:
            print(f"Error loading customer data: {str(e)}")
            return None