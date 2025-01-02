import json
import os
from typing import Dict, Optional
from datetime import datetime
from policy import LifePolicy, CarPolicy, HealthPolicy, PropertyPolicy, PolicyStatus
from policy_enums import PolicyType
from calculations import PolicyCalculator
from customer import Customer


class PolicyJSONHandler:
    DATA_FILE = "data/customer_data.json"  # Correct file path

    @staticmethod
    def ensure_data_directory():
        """Ensure the data directory exists"""
        directory = os.path.dirname(PolicyJSONHandler.DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)

   
    @staticmethod
    def load_policies_from_json(email: str) -> Optional[Customer]:
        """Load policies and customer data for a specific email from the JSON file."""
        try:
            if os.path.exists(PolicyJSONHandler.DATA_FILE):
                with open(PolicyJSONHandler.DATA_FILE, 'r') as f:
                    data = json.load(f)

                if email in data:
                    customer_data = data[email]
                    customer = Customer(
                        email=customer_data["customer_info"]["email"],
                        name=customer_data["customer_info"]["name"],
                        password="",  # Password handling is separate
                        contact_number=customer_data["customer_info"]["contact_number"],
                        address=customer_data["customer_info"]["address"],
                        birth_date=datetime.strptime(customer_data["customer_info"]["birth_date"], "%Y-%m-%d"),
                        credit_score=customer_data["customer_info"]["credit_score"]
                    )

                    # Reconstruct policies
                    for policy_id, policy_info in customer_data.get("policies", {}).items():
                        # Recreate policy instances based on type
                        if policy_info["policy_type"] == "LIFE":
                            policy = LifePolicy(policy_id, email)
                            policy.set_beneficiary(policy_info.get("beneficiary", ""))
                            policy.set_death_benefit(float(policy_info.get("death_benefit", 0)))
                        elif policy_info["policy_type"] == "CAR":
                            policy = CarPolicy(policy_id, email)
                            policy.set_vehicle_details(
                                vehicle_id=policy_info.get("vehicle_id", "N/A"),
                                is_comprehensive=policy_info.get("is_comprehensive", False),
                                vehicle_age=int(policy_info.get("vehicle_age", 0)),
                                vehicle_model=policy_info.get("vehicle_model", "N/A"),
                                vehicle_condition=policy_info.get("vehicle_condition", "N/A"),
                                vehicle_plate_number=policy_info.get("vehicle_plate_number", "UNKNOWN")
                            )
                        elif policy_info["policy_type"] == "HEALTH":
                            policy = HealthPolicy(policy_id, email)
                            policy.set_health_details(
                                deductible=float(policy_info.get("deductible", 0.0)),
                                includes_dental=policy_info.get("includes_dental", False)
                            )
                        elif policy_info["policy_type"] == "PROPERTY":
                            policy = PropertyPolicy(policy_id, email)
                            policy.set_property_details(
                                address=policy_info.get("property_address", "N/A"),
                                property_type=policy_info.get("property_type", "N/A")
                            )
                        else:
                            continue

                        # Set common policy attributes
                        policy.set_coverage_amount(float(policy_info["coverage_amount"]))
                        policy.set_premium(float(policy_info["premium"]))
                        
                        if "status" in policy_info:
                            status_val = str(policy_info["status"])  # force everything to string
                            if status_val.startswith("PolicyStatus."):
                                # e.g. "PolicyStatus.ACTIVE" => parse name after the dot
                                name_part = status_val.split(".")[1]  # ACTIVE
                                policy.update_status(PolicyStatus[name_part])
                            elif status_val.startswith("PolicyStatus("):
                                # e.g. "PolicyStatus(4)" => parse numeric inside parentheses
                                # Remove "PolicyStatus(" and the trailing ")"
                                digit_part = status_val.replace("PolicyStatus(", "").replace(")", "")
                                policy.update_status(PolicyStatus(int(digit_part)))
                            elif status_val.isdigit():
                                # If it’s just a plain digit, e.g. "4"
                                policy.update_status(PolicyStatus(int(status_val)))
                            else:
                                # Otherwise assume it's the direct enum name: "ACTIVE", "PENDING", etc.
                                policy.update_status(PolicyStatus[status_val])

                        
                        # Set dates if available
                        if "start_date" in policy_info and "end_date" in policy_info:
                            policy.set_dates(
                                datetime.strptime(policy_info["start_date"].split('T')[0], "%Y-%m-%d"),
                                datetime.strptime(policy_info["end_date"].split('T')[0], "%Y-%m-%d")
                            )
                            
                        customer.add_policy(policy)

                    return customer
            print(f"No data found for email: {email}")
            return None
        except Exception as e:
            print(f"Error loading policies: {str(e)}")
            return None


    @staticmethod
    def save_policies_to_json(customer: Customer) -> bool:
        """Save customer data and policies to the JSON file."""
        try:
            PolicyJSONHandler.ensure_data_directory()

            # Load existing data from the file
            existing_data = {}
            if os.path.exists(PolicyJSONHandler.DATA_FILE):
                with open(PolicyJSONHandler.DATA_FILE, 'r') as f:
                    existing_data = json.load(f)

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

            # Update with policies
            for policy in customer.policies:
                policy_id = policy.get_policy_id()
                policy_dict = policy.to_dict()
                # Ensure status is converted to string if it's an enum
                if 'status' in policy_dict:
                    policy_dict['status'] = str(policy_dict['status'])
                customer_data["policies"][policy_id] = policy_dict

            # Update the customer data in the existing data
            existing_data[customer.email] = customer_data

            # Save the updated data back to the file
            with open(PolicyJSONHandler.DATA_FILE, 'w') as f:
                json.dump(existing_data, f, indent=4)

            print(f"Policies saved to {PolicyJSONHandler.DATA_FILE}")
            return True
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
            return False
        
    @staticmethod
    def _generate_policy_id() -> str:
        """Generate a unique policy ID"""
        timestamp = int(datetime.now().timestamp())
        return f"POL{timestamp}"

    @staticmethod
    def create_policy_from_request(customer: Customer) -> Optional[Dict]:
        print("\n=== Request New Policy ===")
        PolicyType.display_options()

        try:
            policy_number = int(input("\nEnter policy type number (1-4): "))
            if policy_number not in [ptype.value for ptype in PolicyType]:
                print("Invalid policy type number.")
                return None

            policy_type = PolicyType.get_type_name(policy_number)
            policy_id = PolicyJSONHandler._generate_policy_id()
            coverage_amount = float(input("Enter coverage amount: $"))
            if coverage_amount <= 0:
                print("Coverage amount must be positive.")
                return None

            policy = None
            risk_score = None

            if policy_type == "LIFE":
                policy = LifePolicy(policy_id, customer.email)
                beneficiary = input("Enter Beneficiary Name: ").strip()
                death_benefit = float(input("Enter Death Benefit Amount: $"))
                age = int(input("Enter Insured Person's Age: "))
                health_condition = input("Enter Health Condition (EXCELLENT/GOOD/FAIR/POOR): ").strip().upper()
                is_smoker = input("Is the person a smoker? (y/n): ").lower() == 'y'
                family_history = input("Any family history of serious illness? (y/n): ").lower() == 'y'

                policy.set_beneficiary(beneficiary)
                policy.set_death_benefit(death_benefit)

                risk_score = PolicyCalculator.calculate_life_risk_score(
                    age=age,
                    health_score={"EXCELLENT": 0.2, "GOOD": 0.4, "FAIR": 0.6, "POOR": 0.8}.get(health_condition, 0.5),
                    lifestyle_factors={"smoking": 1.0 if is_smoker else 0.0},
                    family_history=["illness"] if family_history else []
                )

            elif policy_type == "CAR":
                policy = CarPolicy(policy_id, customer.email)
                vehicle_id = f"V{policy_id[3:]}"
                is_comprehensive = input("Is Comprehensive Coverage? (y/n): ").lower() == 'y'
                driver_age = int(input("Enter Driver's Age: "))
                vehicle_model = input("Enter Vehicle Model: ").strip()
                vehicle_age = int(input("Enter Vehicle Age: "))
                vehicle_condition = input("Enter Vehicle Condition (Excellent/Good/Fair/Poor): ").strip()
                accident_count = int(input("Number of accidents in last 5 years: "))
                location_risk = float(input("Enter Location Risk Score (0-1): "))

                policy.set_vehicle_details(
                    vehicle_id=vehicle_id,
                    is_comprehensive=is_comprehensive,
                    vehicle_age=vehicle_age,
                    vehicle_model=vehicle_model,
                    vehicle_condition=vehicle_condition
                )

                risk_score = PolicyCalculator.calculate_car_risk_score(
                    driver_age=driver_age,
                    vehicle_score=vehicle_age * 0.1,  # Simplified example
                    accident_history=[{"date": "2023"} for _ in range(accident_count)],
                    location_risk=location_risk
                )

            elif policy_type == "HEALTH":
                policy = HealthPolicy(policy_id, customer.email)
                deductible = float(input("Enter Deductible Amount: "))
                includes_dental = input("Include Dental Coverage? (y/n): ").lower() == 'y'
                age = int(input("Enter Person's Age: "))
                health_score = float(input("Enter Health Score (0-1, lower is better): "))
                occupation_risk = input("Enter Occupation Risk Level (LOW/MODERATE/HIGH): ").strip().upper()

                policy.set_health_details(deductible, includes_dental)

                risk_score = PolicyCalculator.calculate_health_risk_score(
                    age=age,
                    medical_history={"current_health": health_score},
                    lifestyle_score=0.5,  # Default value
                    occupation_risk={"LOW": 0.2, "MODERATE": 0.5, "HIGH": 0.8}.get(occupation_risk, 0.5)
                )

            elif policy_type == "PROPERTY":
                policy = PropertyPolicy(policy_id, customer.email)
                address = input("Enter Property Address: ").strip()
                property_type = input("Enter Property Type (RESIDENTIAL/COMMERCIAL/INDUSTRIAL): ").strip()
                property_age = int(input("Enter Property Age in Years: "))
                has_security = input("Does the property have security features? (y/n): ").lower() == 'y'
                natural_disaster_risk = float(input("Enter Natural Disaster Risk Score (0-1): "))

                policy.set_property_details(address, property_type)

                risk_score = PolicyCalculator.calculate_property_risk_score(
                    location_data={
                        "natural_disaster": natural_disaster_risk,
                        "crime_rate": 0.5,  # Default value
                        "property_value_trend": 0.5  # Default value
                    },
                    property_details={
                        "construction_quality": 0.7,  # Default value
                        "maintenance": 0.7,
                        "utilities_condition": 0.7
                    },
                    security_score=0.8 if has_security else 0.2,
                    building_age=property_age
                )

            else:
                print("Invalid policy type.")
                return None

            # Set dates
            start_date = datetime.strptime(input("Enter Start Date (YYYY-MM-DD): ").strip(), "%Y-%m-%d")
            end_date = datetime.strptime(input("Enter End Date (YYYY-MM-DD): ").strip(), "%Y-%m-%d")
            policy.set_dates(start_date, end_date)
            policy.set_coverage_amount(coverage_amount)

            # Calculate premium
            premium = PolicyCalculator.calculate_premium(
                PolicyType[policy_type],
                coverage_amount,
                PolicyCalculator.calculate_policy_term(start_date, end_date),  # Calculate term
                {  # Risk factors based on the risk score
                    "base_risk": risk_score.base_score if risk_score else 0.5,
                    "age": risk_score.factors.get("age", 0.0) if risk_score else 0.0
                }
            )
            policy.set_premium(premium)
        

            if customer.add_policy(policy):
                print(f"\nPolicy {policy_id} created successfully!")
                print(f"Calculated Premium: ${premium:,.2f}")
                return policy
            else:
                print("Failed to add policy to customer.")
                return None

        except ValueError as e:
            print(f"Invalid input: {str(e)}")
            return None
        except Exception as e:
            print(f"Error creating policy: {str(e)}")
            return None
