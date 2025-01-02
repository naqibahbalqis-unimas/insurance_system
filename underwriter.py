## underwriter.py
import json
from tabulate import tabulate
from typing import Dict, List, Optional
from datetime import datetime, date
from auth import AuthenticationManager
from policy import Policy, LifePolicy, CarPolicy, HealthPolicy, PropertyPolicy
from policy_enums import PolicyType, PolicyStatus
from claim import Claim
from payment import Payment
from financial_calculator import FinancialCalculator
from policy_json_handler import PolicyJSONHandler
from serialization_handler import SerializationHandler
from customer import Customer  # Add this import

class UnderwriterCLI:
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.current_user = None
        self.policies: Dict[str, Policy] = {}
        self.claims: Dict[str, Claim] = {}
        self.payments: Dict[str, Payment] = {}
        self.calculator = FinancialCalculator()

    def display_menu(self):
        print("\n=== Underwriter Management System ===")
        menu_options = [
            ["1", "View Profile"],
            ["2", "Update Profile"],
            ["3", "Manage Policies"],
            ["4", "Process Claims"],
            ["5", "Handle Payments"],
            ["6", "Financial Calculations"],
            ["7", "Back to Main Menu"]
        ]
        print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="grid"))

    def run(self):
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                self.view_profile()
            elif choice == "2":
                self.update_profile()
            elif choice == "3":
                self.manage_policies()
            elif choice == "4":
                self.process_claims()
            elif choice == "5":
                self.handle_payments()
            elif choice == "6":
                self.financial_calculations()
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")

    def view_profile(self):
        if self.current_user:
            user = self.auth_manager._users.get(self.current_user)
            if user:
                print("\n=== Profile Information ===")
                print(f"Name: {user.name}")
                print(f"Email: {user.email}")
                print(f"Role: {user.role}")
            else:
                print("User information not found.")
        else:
            print("No user currently logged in.")

    def update_profile(self):
        if not self.current_user:
            print("Please log in first.")
            return

        print("\n=== Update Profile ===")
        print("1. Update Name")
        print("2. Update Email")
        print("3. Update Password")
        print("4. Back")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            name = input("Enter new name: ").strip()
            if name:
                self.auth_manager.update_user_details(self.current_user, name=name)
                print("Name updated successfully!")
        elif choice == "2":
            email = input("Enter new email: ").strip()
            if email:
                self.auth_manager.update_user_details(self.current_user, email=email)
                print("Email updated successfully!")
        elif choice == "3":
            old_password = input("Enter current password: ").strip()
            new_password = input("Enter new password: ").strip()
            if self.auth_manager.change_password(self.current_user, old_password, new_password):
                print("Password updated successfully!")
            else:
                print("Failed to update password.")

    def manage_policies(self):
        """Manage policies with automatic loading"""
        # First, load customer policies automatically
        print("\nLoading customer policies...")
        self.load_customer_policies()

        while True:
            print("\n=== Policy Management ===")
            print("1. View All Policies")
            print("2. Create New Policy")
            print("3. Search Policy")
            print("4. Update Policy")
            print("5. Calculate Premium")
            print("6. Save Policies")
            print("7. Load Policies")
            print("8. Back")

            choice = input("\nEnter your choice (1-8): ").strip()

            if choice == "1":
                # For viewing all policies, handle like a customer view
                customer_email = input("\nEnter Customer Email: ").strip()
                customer = PolicyJSONHandler.load_policies_from_json(customer_email)
                if customer:
                    policies = customer.get_policies()
                    self.view_all_policies(policies)
                else:
                    print(f"No policies found for customer: {customer_email}")
            elif choice == "2":
                self.create_new_policy()
            elif choice == "3":
                self.search_policy()
            elif choice == "4":
                self.update_policy()
            elif choice == "5":
                self.calculate_policy_premium()
            elif choice == "6":
                self.save_policies()
            elif choice == "7":
                customer_email = input("\nEnter Customer Email: ").strip()
                customer = PolicyJSONHandler.load_policies_from_json(customer_email)
                if customer:
                    print(f"Successfully loaded policies for {customer_email}")
                    # Store the loaded policies in the underwriter's policies dict
                    for policy in customer.policies:
                        self.policies[policy.get_policy_id()] = policy
                else:
                    print(f"No policies found for {customer_email}")
            elif choice == "8":
                break
            else:
                print("Invalid choice. Please try again.")
                
    def save_policies(self) -> bool:
        """Save policies to the JSON file while preserving status changes"""
        try:
            # Get customer email
            customer_email = input("\nEnter Customer Email: ").strip()
            
            # Load existing customer data
            existing_customer = PolicyJSONHandler.load_policies_from_json(customer_email)
            if not existing_customer:
                existing_customer = Customer(
                    email=customer_email,
                    name=customer_email.split('@')[0],
                    password="",
                    contact_number="",
                    address="",
                    credit_score=0.0
                )
            
            # Create a map of existing policies for quick lookup
            existing_policies = {p.get_policy_id(): p for p in existing_customer.policies}
            
            # Update existing policies with any changes from self.policies
            for policy_id, updated_policy in self.policies.items():
                if updated_policy.customer_id == customer_email:
                    if policy_id in existing_policies:
                        # Update existing policy
                        existing_policy = existing_policies[policy_id]
                        existing_policy.update_status(updated_policy.get_status())
                        existing_policy.set_coverage_amount(updated_policy.get_coverage_amount())
                        existing_policy.set_premium(updated_policy.get_premium())
                    else:
                        # Add new policy
                        existing_customer.add_policy(updated_policy)
            
            # Save the updated customer data
            if PolicyJSONHandler.save_policies_to_json(existing_customer):
                print("All changes successfully saved!")
                return True
            
            print("Failed to save changes.")
            return False
            
        except Exception as e:
            print(f"Error saving policies: {str(e)}")
            print("Details:", str(e.__class__))  # Print the error class for debugging
            return False
    
    def load_customer_policies(self) -> bool:
        """Load policies from customer data file"""
        try:
            loaded_data = SerializationHandler.load_from_json("customer_data.json")
            if not loaded_data:
                print("No data found.")
                return False
                
            if "policies" not in loaded_data:
                print("No policies section found in data.")
                return False

            # Clear existing policies before loading
            self.policies.clear()

            # Get the policies dictionary from the nested structure
            policies_data = loaded_data["policies"]
            if not policies_data:
                print("No policies found in data.")
                return False

            # Convert loaded policy data into Policy objects
            for policy_id, policy_data in policies_data.items():
                policy_type = policy_data.get("policy_type")
                customer_id = policy_data.get("customer_id")

                policy = None
                if policy_type == "LIFE":
                    policy = LifePolicy(policy_id, customer_id)
                    if "beneficiary" in policy_data:
                        policy.set_beneficiary(policy_data["beneficiary"])
                    if "death_benefit" in policy_data:
                        policy.set_death_benefit(float(policy_data["death_benefit"]))
                        
                elif policy_type == "CAR":
                    policy = CarPolicy(policy_id, customer_id)
                    if all(k in policy_data for k in ["vehicle_id", "is_comprehensive", "vehicle_age", 
                                                    "vehicle_model", "vehicle_plate_number", "vehicle_condition"]):
                        policy.set_vehicle_details(
                            policy_data["vehicle_id"],
                            policy_data["is_comprehensive"],
                            policy_data["vehicle_age"],
                            policy_data["vehicle_model"],
                            policy_data["vehicle_plate_number"],
                            policy_data["vehicle_condition"]
                        )
                        
                elif policy_type == "HEALTH":
                    policy = HealthPolicy(policy_id, customer_id)
                    if "deductible" in policy_data and "includes_dental" in policy_data:
                        policy.set_health_details(
                            float(policy_data["deductible"]),
                            policy_data["includes_dental"]
                        )
                        
                elif policy_type == "PROPERTY":
                    policy = PropertyPolicy(policy_id, customer_id)
                    if "property_address" in policy_data and "property_type" in policy_data:
                        policy.set_property_details(
                            policy_data["property_address"],
                            policy_data["property_type"]
                        )

                if policy:
                    # Set common policy attributes
                    if "coverage_amount" in policy_data:
                        policy.set_coverage_amount(float(policy_data["coverage_amount"]))
                    if "premium" in policy_data:
                        policy.set_premium(float(policy_data["premium"]))
                    if "status" in policy_data:
                        try:
                            policy.update_status(PolicyStatus[policy_data["status"]])
                        except (KeyError, ValueError):
                            pass  # Keep default status if invalid

                    # Store the policy
                    self.policies[policy_id] = policy

            print(f"Successfully loaded {len(self.policies)} customer policies.")
            return True
        except Exception as e:
            print(f"Error loading customer policies: {str(e)}")
            return False

    def load_policies(self):
        """Load policies from the hardcoded customer_data.json file"""
        try:
            loaded_policies = PolicyJSONHandler.load_policies_from_json()
            if "policies" in loaded_policies:
                for policy_id, policy_data in loaded_policies["policies"].items():
                    # Create and add policies to self.policies
                    # Logic for initializing specific policies goes here
                    print(f"Loaded policy {policy_id}")
                print("Policies successfully loaded.")
            else:
                print("No policies found in customer_data.json.")
        except Exception as e:
            print(f"Error loading policies: {str(e)}")

    @staticmethod
    def save_policies_to_json(policies_dict: Dict) -> bool:
        """Save policies and customer data to the hardcoded JSON file"""
        try:
            PolicyJSONHandler.ensure_data_directory()
            with open(PolicyJSONHandler.DATA_FILE, 'w') as f:
                json.dump(policies_dict, f, indent=4)
            print(f"Policies saved to {PolicyJSONHandler.DATA_FILE}")
            return True
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
            return False

    
    def create_new_policy(self):
        print("\n=== Create New Policy ===")
        print("Available Policy Types:")
        for policy_type in PolicyType:
            print(f"- {policy_type.name}")

        try:
            policy_type_str = input("\nEnter Policy Type: ").strip().upper()
            if policy_type_str not in PolicyType.__members__:
                print("Invalid policy type.")
                return

            policy_id = input("Enter Policy ID: ").strip()
            customer_id = input("Enter Customer ID: ").strip()
            coverage_amount = float(input("Enter Coverage Amount: "))
            
            # Collect policy-specific details
            if policy_type_str == "LIFE":
                policy = LifePolicy(policy_id, customer_id)
                beneficiary = input("Enter Beneficiary Name: ").strip()
                death_benefit = float(input("Enter Death Benefit Amount: "))
                age = int(input("Enter Insured Person's Age: "))
                health_condition = input("Enter Health Condition (EXCELLENT/GOOD/FAIR/POOR): ").strip().upper()
                is_smoker = input("Is the person a smoker? (y/n): ").lower() == 'y'
                family_history = input("Any family history of serious illness? (y/n): ").lower() == 'y'
                
                policy.set_beneficiary(beneficiary)
                policy.set_death_benefit(death_benefit)
                
                risk_score = self.calculator.calculate_life_risk_score(
                    age=age,
                    health_score={"EXCELLENT": 0.2, "GOOD": 0.4, "FAIR": 0.6, "POOR": 0.8}.get(health_condition, 0.5),
                    lifestyle_factors={"smoking": 1.0 if is_smoker else 0.0},
                    family_history=["illness"] if family_history else []
                )

            elif policy_type_str == "CAR":
                policy = CarPolicy(policy_id, customer_id)
                vehicle_id = input("Enter Vehicle ID: ").strip()
                is_comprehensive = input("Is Comprehensive Coverage? (y/n): ").lower() == 'y'
                driver_age = int(input("Enter Driver's Age: "))
                vehicle_score = float(input("Enter Vehicle Score (0-1, higher for more expensive/risky vehicles): "))
                accident_count = int(input("Number of accidents in last 5 years: "))
                location_risk = float(input("Enter Location Risk Score (0-1): "))
                
                policy.set_vehicle_details(vehicle_id, is_comprehensive)
                
                risk_score = self.calculator.calculate_car_risk_score(
                    driver_age=driver_age,
                    vehicle_score=vehicle_score,
                    accident_history=[{"date": "2023"} for _ in range(accident_count)],
                    location_risk=location_risk
                )

            elif policy_type_str == "HEALTH":
                policy = HealthPolicy(policy_id, customer_id)
                deductible = float(input("Enter Deductible Amount: "))
                includes_dental = input("Include Dental Coverage? (y/n): ").lower() == 'y'
                age = int(input("Enter Person's Age: "))
                health_score = float(input("Enter Health Score (0-1, lower is better): "))
                occupation_risk = input("Enter Occupation Risk Level (LOW/MODERATE/HIGH): ").strip().upper()
                
                policy.set_health_details(deductible, includes_dental)
                
                risk_score = self.calculator.calculate_health_risk_score(
                    age=age,
                    medical_history={"current_health": health_score},
                    lifestyle_score=0.5,  # Default value, could be made more detailed
                    occupation_risk={"LOW": 0.2, "MODERATE": 0.5, "HIGH": 0.8}.get(occupation_risk, 0.5)
                )

            elif policy_type_str == "PROPERTY":
                policy = PropertyPolicy(policy_id, customer_id)
                address = input("Enter Property Address: ").strip()
                property_type = input("Enter Property Type (RESIDENTIAL/COMMERCIAL/INDUSTRIAL): ").strip()
                property_age = int(input("Enter Property Age in Years: "))
                has_security = input("Does property have security features? (y/n): ").lower() == 'y'
                natural_disaster_risk = float(input("Enter Natural Disaster Risk Score (0-1): "))
                
                policy.set_property_details(address, property_type)
                
                risk_score = self.calculator.calculate_property_risk_score(
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

            # Set dates
            start_date_str = input("Enter Start Date (YYYY-MM-DD): ")
            end_date_str = input("Enter End Date (YYYY-MM-DD): ")
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            policy.set_dates(start_date, end_date)
            policy.set_coverage_amount(coverage_amount)

            # Calculate premium using risk score
            premium = self.calculator.calculate_premium(
                PolicyType[policy_type_str],
                coverage_amount,
                risk_score
            )
            policy.set_premium(premium)

            if policy.validate_policy():
                self.policies[policy_id] = policy
                print(f"\nPolicy created successfully! Policy ID: {policy_id}")
                print(f"Calculated Premium: ${premium:,.2f}")
                print("\nRisk Assessment:")
                print(f"Base Score: {risk_score.base_score:.2f}")
                print(f"Confidence: {risk_score.confidence:.2%}")
                print("\nRisk Factors:")
                for factor, value in risk_score.factors.items():
                    print(f"- {factor.title()}: {value:.2f}")
                
                # Auto-save after creating policy
                if PolicyJSONHandler.save_policies_to_json(self.policies, "policies"):
                    print("\nPolicy automatically saved to data/customer_data.json")
                else:
                    print("\nWarning: Failed to auto-save policy. You may need to save manually.")
            else:
                print("Policy validation failed. Please check all details.")

        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"Error creating policy: {str(e)}")
            
    def load_policies(self):
        """Load policies from a JSON file"""
        try:
            filename = input("Enter filename to load policies from: ").strip()
            if not filename.endswith('.json'):
                filename += '.json'
                
            loaded_data = SerializationHandler.load_from_json(filename)
            if not loaded_data or "policies" not in loaded_data:
                print("No valid policy data found in file.")
                return

            # Clear existing policies
            self.policies.clear()
            
            # Get only the policies section
            policies_data = loaded_data["policies"]
            
            print("\n=== Loading Policies ===")
            for policy_id, policy_data in policies_data.items():
                try:
                    policy_type = policy_data.get("policy_type")
                    customer_id = policy_data.get("customer_id")
                    
                    # Create appropriate policy object
                    if policy_type == "LIFE":
                        policy = LifePolicy(policy_id, customer_id)
                        if "beneficiary" in policy_data:
                            policy.set_beneficiary(policy_data["beneficiary"])
                        if "death_benefit" in policy_data:
                            policy.set_death_benefit(float(policy_data["death_benefit"]))
                    elif policy_type == "CAR":
                        policy = CarPolicy(policy_id, customer_id)
                        # Set car-specific details
                    elif policy_type == "HEALTH":
                        policy = HealthPolicy(policy_id, customer_id)
                        if "deductible" in policy_data and "includes_dental" in policy_data:
                            policy.set_health_details(
                                float(policy_data["deductible"]),
                                policy_data["includes_dental"]
                            )
                    elif policy_type == "PROPERTY":
                        policy = PropertyPolicy(policy_id, customer_id)
                        if "property_address" in policy_data and "property_type" in policy_data:
                            policy.set_property_details(
                                policy_data["property_address"],
                                policy_data["property_type"]
                            )
                    else:
                        continue

                    # Set common attributes
                    if "coverage_amount" in policy_data:
                        policy.set_coverage_amount(float(policy_data["coverage_amount"]))
                    if "premium" in policy_data:
                        policy.set_premium(float(policy_data["premium"]))
                    if "status" in policy_data:
                        policy.update_status(PolicyStatus[policy_data["status"]])

                    self.policies[policy_id] = policy
                    print(f"Loaded policy {policy_id} ({policy_type})")

                except Exception as e:
                    print(f"Error loading policy {policy_id}: {str(e)}")
                    continue

            print(f"\nSuccessfully loaded {len(self.policies)} policies.")
            return True
        except Exception as e:
            print(f"Error loading policies: {str(e)}")
            return False
    def view_all_policies(self, policies):
        """Display all policies with their details"""
        if not policies:
            print("\nNo policies found.")
            return

        print("\n=== All Policies ===")
        for policy in policies:
            print(f"\nPolicy ID: {policy['policy_id']}")
            print(f"Type: {policy['policy_type']}")
            print(f"Status: {policy['status']}")
            print(f"Coverage: ${float(policy['coverage_amount']):,.2f}")
            print(f"Premium: ${float(policy['premium']):,.2f}")
            
            # Display policy-specific details
            if policy['policy_type'] == 'LIFE':
                print(f"Beneficiary: {policy.get('beneficiary', 'N/A')}")
                print(f"Death Benefit: ${float(policy.get('death_benefit', 0)):,.2f}")
            elif policy['policy_type'] == 'CAR':
                print(f"Vehicle ID: {policy.get('vehicle_id', 'N/A')}")
                print(f"Vehicle Model: {policy.get('vehicle_model', 'N/A')}")
                print(f"Comprehensive: {'Yes' if policy.get('is_comprehensive', False) else 'No'}")
            elif policy['policy_type'] == 'HEALTH':
                print(f"Deductible: ${float(policy.get('deductible', 0)):,.2f}")
                print(f"Includes Dental: {'Yes' if policy.get('includes_dental', False) else 'No'}")
            elif policy['policy_type'] == 'PROPERTY':
                print(f"Property Address: {policy.get('property_address', 'N/A')}")
                print(f"Property Type: {policy.get('property_type', 'N/A')}")
            print("----------------------------------------")
  
    def _get_risk_factors(self) -> Dict[str, float]:
        print("\nEnter risk factors (0-1, where 0 is lowest risk):")
        risk_factors = {}
        try:
            risk_factors['age'] = float(input("Age factor: "))
            risk_factors['health'] = float(input("Health factor: "))
            risk_factors['occupation'] = float(input("Occupation factor: "))
            # Validate risk factors are between 0 and 1
            for key, value in risk_factors.items():
                if not 0 <= value <= 1:
                    raise ValueError(f"Risk factor {key} must be between 0 and 1")
        except ValueError as e:
            print(f"Invalid input: {str(e)}")
            return {}
        return risk_factors
  
    def search_policy(self):
        policy_id = input("\nEnter Policy ID: ").strip()
        policy = self.policies.get(policy_id)
        
        if policy:
            policy_data = policy.to_dict()
            print("\n=== Policy Details ===")
            for key, value in policy_data.items():
                if isinstance(value, float):
                    print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print("Policy not found.")
    def update_policy(self):
        policy_id = input("\nEnter Policy ID: ").strip()
        customer_email = input("Enter Customer Email: ").strip()

        # Load the policy data from JSON
        customer = PolicyJSONHandler.load_policies_from_json(customer_email)
        if not customer:
            print("Customer not found.")
            return

        # Find the specific policy
        policy_data = None
        for p in customer.policies:
            if p.get_policy_id() == policy_id:
                policy_data = p
                break

        if not policy_data:
            print("Policy not found.")
            return

        # Display current policy details
        print("\n=== Current Policy Details ===")
        print(f"Policy ID: {policy_data.get_policy_id()}")
        print(f"Type: {policy_data.get_policy_type().name}")
        print(f"Status: {policy_data.get_status().name}")
        print(f"Coverage: ${policy_data.get_coverage_amount():,.2f}")

        print("\n=== Update Policy ===")
        print("1. Update Status")
        print("2. Update Coverage Amount")
        print("3. Back")

        choice = input("\nEnter your choice (1-3): ").strip()

        try:
            if choice == "1":
                print("\nAvailable Statuses:")
                for status in PolicyStatus:
                    print(f"{status.value}. {status.name}")

                new_status_value = int(input("\nEnter new status number: "))
                if new_status_value not in [status.value for status in PolicyStatus]:
                    print("Invalid status number.")
                    return

                new_status = PolicyStatus(new_status_value)
                policy_data.update_status(new_status)
                print(f"Status updated to {new_status.name}")

            elif choice == "2":
                new_coverage = float(input("Enter new coverage amount: $"))
                if new_coverage <= 0:
                    print("Coverage amount must be positive.")
                    return

                policy_data.set_coverage_amount(new_coverage)
                print("Coverage amount updated successfully!")

            elif choice == "3":
                return

            else:
                print("Invalid choice.")
                return

            # Save the updated customer data
            if PolicyJSONHandler.save_policies_to_json(customer):
                print("Changes saved successfully!")
            else:
                print("Failed to save changes.")

        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"Error updating policy: {str(e)}")

    def calculate_policy_premium(self):
            policy_id = input("\nEnter Policy ID: ").strip()
            policy = self.policies.get(policy_id)
            
            if not policy:
                print("Policy not found.")
                return

            try:
                risk_factors = self._get_risk_factors()
                premium = policy.calculate_premium(risk_factors)
                print(f"\nCalculated Premium: ${premium:,.2f}")
            except Exception as e:
                print(f"Error calculating premium: {str(e)}")

    def process_claims(self):
        print("\n=== Claims Processing ===")
        print("1. View Pending Claims")
        print("2. Review Claim")
        print("3. Calculate Claim Payout")
        print("4. Back")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            self.view_pending_claims()
        elif choice == "2":
            self.review_claim()
        elif choice == "3":
            self.calculate_claim_payout()

    def view_pending_claims(self):
        pending_claims = [claim for claim in self.claims.values() 
                         if claim.get_status() == "PENDING"]
        
        if not pending_claims:
            print("No pending claims found.")
            return

        print("\n=== Pending Claims ===")
        for claim in pending_claims:
            print(f"\nClaim ID: {claim.get_claim_id()}")
            print(f"Policy ID: {claim.policy_id}")
            print(f"Amount: ${claim.get_amount():,.2f}")
            print(f"Description: {claim.get_description()}")
            if claim.evidence_documents:
                print("Evidence Documents:")
                for doc in claim.evidence_documents:
                    print(f"- {doc}")

    def review_claim(self):
        claim_id = input("\nEnter Claim ID: ").strip()
        claim = self.claims.get(claim_id)
        
        if not claim:
            print("Claim not found.")
            return

        print(f"\nClaim Amount: ${claim.get_amount():,.2f}")
        print(f"Description: {claim.get_description()}")
        
        action = input("\nAction (APPROVE/REJECT): ").strip().upper()
        if action in ["APPROVE", "REJECT"]:
            if claim.set_status(action):
                print(f"Claim {action.lower()}d successfully.")
                if action == "APPROVE":
                    self.initiate_payment(claim)
            else:
                print("Failed to update claim status.")
        else:
            print("Invalid action.")

    def calculate_claim_payout(self):
        try:
            claim_amount = float(input("Enter claim amount: "))
            coverage_amount = float(input("Enter coverage amount: "))
            deductible = float(input("Enter deductible amount: "))

            payout = FinancialCalculator.calculate_claim_payout(
                claim_amount, coverage_amount, deductible
            )
            print(f"\nCalculated Payout: ${payout:,.2f}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")

    def handle_payments(self):
        print("\n=== Payment Management ===")
        print("1. View Pending Payments")
        print("2. Process Payment")
        print("3. Generate Payment Receipt")
        print("4. Handle Refund")
        print("5. Back")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            self.view_pending_payments()
        elif choice == "2":
            self.process_payment()
        elif choice == "3":
            self.generate_receipt()
        elif choice == "4":
            self.handle_refund()

    def view_pending_payments(self):
        pending_payments = [payment for payment in self.payments.values() 
                          if payment.get_status() == "PENDING"]
        
        if not pending_payments:
            print("No pending payments found.")
            return

        print("\n=== Pending Payments ===")
        for payment in pending_payments:
            print(f"\nPayment ID: {payment.get_payment_id()}")
            print(f"Amount: ${payment.get_amount():,.2f}")
            print(f"Method: {payment.get_payment_method()}")

    def process_payment(self):
        payment_id = input("\nEnter Payment ID: ").strip()
        payment = self.payments.get(payment_id)
        
        if not payment:
            print("Payment not found.")
            return

        print(f"\nAmount: ${payment.get_amount():,.2f}")
        
        method = input("Enter payment method (BANK_TRANSFER/CREDIT_CARD/CHECK): ").strip().upper()
        if payment.set_payment_method(method):
            if payment.process_payment():
                print("Payment processed successfully.")
                if payment.verify_payment():
                    print("Payment verified.")
                else:
                    print("Payment verification failed.")
            else:
                print("Failed to process payment.")
        else:
            print("Invalid payment method.")

    def generate_receipt(self):
        payment_id = input("\nEnter Payment ID: ").strip()
        payment = self.payments.get(payment_id)
        
        if not payment:
            print("Payment not found.")
            return

        receipt = payment.generate_receipt()
        print("\n=== Payment Receipt ===")
        for key, value in receipt.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def handle_refund(self):
        payment_id = input("\nEnter Payment ID: ").strip()
        payment = self.payments.get(payment_id)
        
        if not payment:
            print("Payment not found.")
            return

        if payment.get_status() != "COMPLETED":
            print("Only completed payments can be refunded.")
            return

        amount = payment.get_amount()
        refund_amount = FinancialCalculator.calculate_refund_amount(amount)
        
        confirm = input(f"\nRefund amount will be ${refund_amount:,.2f}. Proceed? (y/n): ").strip().lower()
        if confirm == 'y':
            if payment.refund_payment():
                print("Refund processed successfully.")
            else:
                print("Failed to process refund.")

    def financial_calculations(self):
        print("\n=== Financial Calculations ===")
        print("1. Calculate Premium")
        print("2. Validate Payment")
        print("3. Back")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            self.calculate_premium()
        elif choice == "2":
            self.validate_payment()

    def calculate_premium(self):
        try:
            policy_type = input("Enter policy type (LIFE/CAR/HEALTH/PROPERTY): ").strip().upper()
            coverage_amount = float(input("Enter coverage amount: "))
            
            print("\nEnter risk factors (as decimal, e.g., 0.1 for 10% risk):")
            risk_factors = {}
            risk_factors['age'] = float(input("Age factor: "))
            risk_factors['health'] = float(input("Health factor: "))

            premium = FinancialCalculator.calculate_premium(
                policy_type,
                coverage_amount,
                risk_factors
            )
            print(f"\nCalculated Premium: ${premium:,.2f}")
        except ValueError:
            print("Invalid input. Please enter numeric values for amounts and risk factors.")

    def validate_payment(self):
        try:
            payment_amount = float(input("Enter payment amount: "))
            claim_amount = float(input("Enter claim amount: "))

            if FinancialCalculator.validate_payment_amount(payment_amount, claim_amount):
                print("Payment amount is valid.")
            else:
                print("Payment amount does not match claim amount.")
        except ValueError:
            print("Invalid input. Please enter numeric values.")

    def initiate_payment(self, claim: Claim):
        payment_id = f"PAY_{claim.get_claim_id()}"
        payment = Payment(payment_id, claim.policy_id)
        
        if payment.set_amount(claim.get_amount()):
            self.payments[payment_id] = payment
            print(f"Payment initiated. Payment ID: {payment_id}")
        else:
            print("Failed to initiate payment.")