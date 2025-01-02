# policy_request_templates.py

"""
This module contains template JSON structures for different types of policy requests.
These templates can be used as a base for creating new policy requests or for validation.
"""

from typing import Dict

def get_life_policy_template() -> Dict:
    return {
        "policy_type": "LIFE",
        "customer_info": {
            "customer_id": "johndoe@example.com",
            "name": "John Doe",
            "birth_date": "1990-01-01",
            "contact_number": "1234567890",
            "address": "123 Main Street",
            "credit_score": 750.0
        },
        "policy_details": {
            "policy_id": "POL123",
            "coverage_amount": 100000.0,
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "conditions": ["Non-smoker", "No pre-existing conditions"]
        },
        "life_policy_specific": {
            "beneficiary": "Jane Doe",
            "death_benefit": 100000.0,
            "risk_factors": {
                "age": 30,
                "health_condition": "Excellent",
                "occupation_risk": "Low"
            }
        }
    }

def get_car_policy_template() -> Dict:
    return {
        "policy_type": "CAR",
        "customer_info": {
            "customer_id": "johndoe@example.com",
            "name": "John Doe",
            "birth_date": "1990-01-01",
            "contact_number": "1234567890",
            "address": "123 Main Street",
            "credit_score": 750.0
        },
        "policy_details": {
            "policy_id": "POL124",
            "coverage_amount": 50000.0,
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "conditions": ["Regular maintenance required", "No commercial use"]
        },
        "car_policy_specific": {
            "vehicle_id": "VIN123456789",
            "is_comprehensive": True,
            "vehicle_details": {
                "vehicle_age": 5,
                "vehicle_model": "Toyota Camry",
                "vehicle_plate_number": "ABC123",
                "vehicle_condition": "Excellent",
                "mileage": 50000,
                "security_features": ["Anti-theft", "GPS tracking"]
            },
            "risk_factors": {
                "driving_history": "Clean",
                "parking_location": "Garage",
                "annual_mileage": 12000
            }
        }
    }

def get_health_policy_template() -> Dict:
    return {
        "policy_type": "HEALTH",
        "customer_info": {
            "customer_id": "johndoe@example.com",
            "name": "John Doe",
            "birth_date": "1990-01-01",
            "contact_number": "1234567890",
            "address": "123 Main Street",
            "credit_score": 750.0
        },
        "policy_details": {
            "policy_id": "POL125",
            "coverage_amount": 200000.0,
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "conditions": ["Annual checkup required", "Pre-authorization for non-emergency procedures"]
        },
        "health_policy_specific": {
            "deductible": 1000.0,
            "includes_dental": True,
            "coverage_options": {
                "prescription_coverage": True,
                "mental_health_coverage": True,
                "maternity_coverage": True
            },
            "risk_factors": {
                "pre_existing_conditions": [],
                "family_history": "No major conditions",
                "lifestyle": "Active"
            }
        }
    }

def get_property_policy_template() -> Dict:
    return {
        "policy_type": "PROPERTY",
        "customer_info": {
            "customer_id": "johndoe@example.com",
            "name": "John Doe",
            "birth_date": "1990-01-01",
            "contact_number": "1234567890",
            "address": "123 Main Street",
            "credit_score": 750.0
        },
        "policy_details": {
            "policy_id": "POL126",
            "coverage_amount": 300000.0,
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "conditions": ["Security system required", "Regular maintenance required"]
        },
        "property_policy_specific": {
            "property_address": "456 Oak Street",
            "property_type": "Single Family Home",
            "property_details": {
                "year_built": 2000,
                "square_footage": 2000,
                "construction_type": "Frame",
                "number_of_floors": 2,
                "security_features": ["Alarm System", "Smoke Detectors"]
            },
            "risk_factors": {
                "location_risk": "LOW",
                "flood_zone": False,
                "previous_claims": 0
            }
        }
    }

# Helper function to get template by policy type
def get_policy_template(policy_type: str) -> Dict:
    """
    Get a policy template by policy type
    
    Args:
        policy_type: String representing the policy type (LIFE, CAR, HEALTH, PROPERTY)
        
    Returns:
        Dict containing the template for the specified policy type
        
    Raises:
        ValueError if policy type is not recognized
    """
    templates = {
        "LIFE": get_life_policy_template,
        "CAR": get_car_policy_template,
        "HEALTH": get_health_policy_template,
        "PROPERTY": get_property_policy_template
    }
    
    if policy_type.upper() not in templates:
        raise ValueError(f"Unknown policy type: {policy_type}")
        
    return templates[policy_type.upper()]()