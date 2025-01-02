from datetime import datetime, date
from typing import List, Dict, Optional
from users import User
from policy import Policy, LifePolicy, CarPolicy, HealthPolicy, PropertyPolicy, PolicyManager
from claim import Claim
from policy_enums import PolicyStatus, PolicyType
from serialization_handler import SerializationHandler
from policy_calculator import PolicyCalculator
from data_storage_service import DataStorageService


class Customer(User):
    def __init__(
        self,
        email: str,
        name: str,
        password: str,
        contact_number: str = "",
        address: str = "",
        birth_date: Optional[date] = None,
        credit_score: float = 0.0
    ):
        super().__init__(email)
        self.name = name
        self.password = password
        self._contact_number = contact_number  # Private contact number
        self.address = address  # Customer's address
        self.birth_date = birth_date or date.today()  # Customer's birth date
        self.credit_score = credit_score  # Customer's credit score
        self.policies: List[Policy] = []  # List of policies associated with the customer
        self.claims: List[Claim] = []  # List of claims associated with the customer

    @classmethod
    def from_dict(cls, data: Dict) -> Optional['Customer']:
        """Create a Customer instance from dictionary data."""
        try:
            customer_info = data["customer_info"]
            customer = cls(
                email=customer_info["email"],
                name=customer_info["name"],
                password="",  # Password handling is separate
                contact_number=customer_info["contact_number"],
                address=customer_info["address"],
                birth_date=datetime.strptime(customer_info["birth_date"], "%Y-%m-%d"),
                credit_score=float(customer_info["credit_score"])
            )

            # Add policies if present
            if "policies" in data:
                for policy_id, policy_data in data["policies"].items():
                    policy_type = policy_data["policy_type"]
                    if policy_type == "LIFE":
                        policy = LifePolicy(policy_id, customer_info["email"])
                        policy.set_beneficiary(policy_data.get("beneficiary", ""))
                        policy.set_death_benefit(float(policy_data.get("death_benefit", 0)))
                    elif policy_type == "CAR":
                        policy = CarPolicy(policy_id, customer_info["email"])
                        # Handle potential missing vehicle_plate_number in old data
                        vehicle_details = {
                            "vehicle_id": policy_data.get("vehicle_id", "N/A"),
                            "is_comprehensive": policy_data.get("is_comprehensive", False),
                            "vehicle_age": int(policy_data.get("vehicle_age", 0)),
                            "vehicle_model": policy_data.get("vehicle_model", "N/A"),
                            "vehicle_condition": policy_data.get("vehicle_condition", "N/A"),
                            "vehicle_plate_number": policy_data.get("vehicle_plate_number", "UNKNOWN")
                        }
                        policy.set_vehicle_details(**vehicle_details)
                    elif policy_type == "HEALTH":
                        policy = HealthPolicy(policy_id, customer_info["email"])
                        policy.set_health_details(
                            deductible=float(policy_data.get("deductible", 0.0)),
                            includes_dental=policy_data.get("includes_dental", False)
                        )
                    elif policy_type == "PROPERTY":
                        policy = PropertyPolicy(policy_id, customer_info["email"])
                        policy.set_property_details(
                            address=policy_data.get("property_address", "N/A"),
                            property_type=policy_data.get("property_type", "N/A")
                        )
                    else:
                        continue

                    policy.set_coverage_amount(float(policy_data["coverage_amount"]))
                    policy.set_premium(float(policy_data["premium"]))
                    if "status" in policy_data:
                        policy.update_status(PolicyStatus[policy_data["status"]])
                    if "start_date" in policy_data:
                        policy.set_dates(
                            datetime.strptime(policy_data["start_date"].split('T')[0], "%Y-%m-%d"),
                            datetime.strptime(policy_data["end_date"].split('T')[0], "%Y-%m-%d")
                        )
                    customer.add_policy(policy)

                return customer
            return customer
        except Exception as e:
            print(f"Error creating customer from dict: {str(e)}")
            return None
    def add_policy(self, policy: Policy) -> bool:
        """Add a new policy for the customer"""
        if policy and policy.customer_id == self.email:
            self.policies.append(policy)
            return True
        return False

    def get_policies(self) -> List[Dict]:
        """Retrieve all policies as a list of dictionaries"""
        return [policy.to_dict() for policy in self.policies]

    def calculate_total_premium(self) -> float:
        """Calculate the total premium for all policies"""
        return sum(policy.get_premium() for policy in self.policies)

    def calculate_total_coverage(self) -> float:
        """Calculate the total coverage amount for all policies"""
        return sum(policy.get_coverage_amount() for policy in self.policies)

    def update_contact_info(self, contact_number: str = None, address: str = None) -> bool:
        """Update the customer's contact information"""
        if contact_number:
            self._contact_number = contact_number
        if address:
            self.address = address
        return True

    def add_claim(self, claim: Claim) -> bool:
        """Add a new claim for the customer"""
        if claim and claim.customer_id == self.email:
            # Validate policy exists and is active
            policy = next((p for p in self.policies if p.get_policy_id() == claim.policy_id), None)
            if not policy or policy.get_status() != PolicyStatus.ACTIVE:
                return False

            self.claims.append(claim)
            return True
        return False

    def get_claims(self) -> List[Dict]:
        """Retrieve all claims as a list of dictionaries"""
        return [claim.to_dict() for claim in self.claims]

    def display_policy_choices(self):
        """Display available policy choices with their details"""
        print("\n=== Available Policies ===")
        for policy in self.policies:
            print(f"Policy ID: {policy.get_policy_id()}, Type: {policy.get_policy_type().name}, Status: {policy.get_status()}")

    def approve_policy(self, policy_id: str, status: PolicyStatus) -> bool:
        """Approve or reject a policy for the customer"""
        policy = next((p for p in self.policies if p.get_policy_id() == policy_id), None)
        if policy and status in [PolicyStatus.APPROVED, PolicyStatus.REJECTED]:
            return policy.update_status(status)
        return False

    def __str__(self):
        return (f"Customer Email: {self.email}, Name: {self.name}, Address: {self.address}, "
                f"Birth Date: {self.birth_date}, Credit Score: {self.credit_score}, "
                f"Total Premium: {self.calculate_total_premium():.2f}, "
                f"Total Claims: {len(self.claims)}")
    def save_to_json(self, filename: str) -> bool:
        """Save customer data and policies to JSON"""
        try:
            customer_data = {
                "customer_info": {
                    "email": self.email,
                    "name": self.name,
                    "contact_number": self._contact_number,
                    "address": self.address,
                    "birth_date": self.birth_date.strftime("%Y-%m-%d"),
                    "credit_score": self.credit_score
                },
                "policies": {
                    policy.get_policy_id(): policy.to_dict()
                    for policy in self.policies
                }
            }
            return SerializationHandler.save_to_json(customer_data, filename)
        except Exception as e:
            print(f"Error saving customer data: {str(e)}")
            return False

    @classmethod
    def load_from_json(cls, filename: str) -> 'Customer':
        """Load customer data and policies from JSON"""
        try:
            data = SerializationHandler.load_from_json(filename)
            if not data or "customer_info" not in data:
                raise ValueError("Invalid customer data format")

            # Create customer instance
            customer_info = data["customer_info"]
            customer = cls(
                email=customer_info["email"],
                name=customer_info["name"],
                password="",  # Password should be handled separately
                contact_number=customer_info["contact_number"],
                address=customer_info["address"],
                birth_date=datetime.strptime(customer_info["birth_date"], "%Y-%m-%d"),
                credit_score=float(customer_info["credit_score"])
            )

            # Add policies if present
            if "policies" in data:
                for policy_id, policy_data in data["policies"].items():
                    policy_type = policy_data["policy_type"]
                    if policy_type == "LIFE":
                        policy = LifePolicy(policy_id, customer_info["email"])
                    elif policy_type == "CAR":
                        policy = CarPolicy(policy_id, customer_info["email"])
                    elif policy_type == "HEALTH":
                        policy = HealthPolicy(policy_id, customer_info["email"])
                    elif policy_type == "PROPERTY":
                        policy = PropertyPolicy(policy_id, customer_info["email"])
                    else:
                        continue

                    policy.set_coverage_amount(float(policy_data["coverage_amount"]))
                    policy.set_premium(float(policy_data["premium"]))
                    if "status" in policy_data:
                        policy.update_status(PolicyStatus[policy_data["status"]])

                    # Set additional details based on policy type
                    if isinstance(policy, LifePolicy):
                        policy.set_beneficiary(policy_data.get("beneficiary", "N/A"))
                        policy.set_death_benefit(float(policy_data.get("death_benefit", 0.0)))
                    elif isinstance(policy, CarPolicy):
                        policy.set_vehicle_details(
                            vehicle_id=policy_data.get("vehicle_id", "N/A"),
                            is_comprehensive=policy_data.get("is_comprehensive", False),
                            vehicle_age=int(policy_data.get("vehicle_age", 0)),
                            vehicle_model=policy_data.get("vehicle_model", "N/A"),
                            vehicle_plate_number=policy_data.get("vehicle_plate_number", "N/A"),
                            vehicle_condition=policy_data.get("vehicle_condition", "N/A")
                        )
                    elif isinstance(policy, HealthPolicy):
                        policy.set_health_details(
                            deductible=float(policy_data.get("deductible", 0.0)),
                            includes_dental=policy_data.get("includes_dental", False)
                        )
                    elif isinstance(policy, PropertyPolicy):
                        policy.set_property_details(
                            address=policy_data.get("property_address", "N/A"),
                            property_type=policy_data.get("property_type", "N/A")
                        )

                    customer.add_policy(policy)

            return customer
        except Exception as e:
            print(f"Error loading customer data: {str(e)}")
            return None

class CustomerCLI:
    def __init__(self, customer: Customer):
        self.customer = customer
        self.policy_manager = PolicyManager()
        self._policy_counter = 1
        self._claim_counter = 1
        self._policy_counter = DataStorageService.get_highest_policy_number() + 1
        self._claim_counter = 1
        self._update_counters()  # Initialize counters based on existing policies/claims


    def _update_counters(self):
        """Update the counters based on existing policies and claims"""
        # Update policy counter
        for policy in self.customer.policies:
            try:
                policy_num = int(policy.policy_id[3:])  # Extract number from POLxxx
                self._policy_counter = max(self._policy_counter, policy_num + 1)
            except (ValueError, IndexError):
                continue

        # Update claim counter
        for claim in self.customer.claims:
            try:
                claim_num = int(claim.claim_id[3:])  # Extract number from CLMxxx
                self._claim_counter = max(self._claim_counter, claim_num + 1)
            except (ValueError, IndexError):
                continue
    def _generate_policy_id(self) -> str:
        """Generate a unique policy ID"""
        policy_id = f"POL{self._policy_counter:03d}"
        self._policy_counter += 1
        return policy_id

    def _generate_claim_id(self) -> str:
        """Generate a unique claim ID"""
        claim_id = f"CLM{self._claim_counter:03d}"
        self._claim_counter += 1
        return claim_id


    def request_new_policy(self):
        print("\n=== Request New Policy ===")
        print("Available Policy Types:")
        PolicyType.display_options()

        try:
            policy_number = int(input("\nEnter policy type number (1-4): "))
            if policy_number not in [ptype.value for ptype in PolicyType]:
                print("Invalid policy type number.")
                return

            policy_type = PolicyType.get_type_name(policy_number)
            policy_id = self._generate_policy_id()
            customer_id = self.customer.email
            coverage_amount = float(input("Enter coverage amount: $"))
            if coverage_amount <= 0:
                print("Coverage amount must be positive.")
                return

            policy = None
            risk_score = None

            # Collect policy-specific details
            if policy_type == "LIFE":
                policy = LifePolicy(policy_id, customer_id)
                beneficiary = input("Enter Beneficiary Name: ").strip()
                death_benefit = float(input("Enter Death Benefit Amount: "))
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
                vehicle_id = f"V{policy_id[3:]}"
                is_comprehensive = input("Is Comprehensive Coverage? (y/n): ").lower() == 'y'
                driver_age = int(input("Enter Driver's Age: "))
                vehicle_model = input("Enter Vehicle Model: ").strip()
                vehicle_age = int(input("Enter Vehicle Age: "))
                vehicle_condition = input("Enter Vehicle Condition (Excellent/Good/Fair/Poor): ").strip()
                accident_count = int(input("Number of accidents in last 5 years: "))
                location_risk = float(input("Enter Location Risk Score (0-1): "))
                vehicle_plate_number = input("Enter Vehicle Plate Number: ").strip()

                policy = CarPolicy(policy_id, customer_id)
                policy.set_vehicle_details(
                    vehicle_id=vehicle_id,
                    is_comprehensive=is_comprehensive,
                    vehicle_age=vehicle_age,
                    vehicle_model=vehicle_model,
                    vehicle_plate_number=vehicle_plate_number,
                    vehicle_condition=vehicle_condition
                )

                risk_score = PolicyCalculator.calculate_car_risk_score(
                    driver_age=driver_age,
                    vehicle_score=vehicle_age * 0.1,  # Simplified example
                    accident_history=[{"date": "2023"} for _ in range(accident_count)],
                    location_risk=location_risk
                )

            elif policy_type == "HEALTH":
                policy = HealthPolicy(policy_id, customer_id)
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
                policy = PropertyPolicy(policy_id, customer_id)
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
                return

            # Set dates
            start_date = datetime.strptime(input("Enter Start Date (YYYY-MM-DD): ").strip(), "%Y-%m-%d")
            end_date = datetime.strptime(input("Enter End Date (YYYY-MM-DD): ").strip(), "%Y-%m-%d")
            policy.set_dates(start_date, end_date)
            policy.set_coverage_amount(coverage_amount)

            # Calculate premium
            term_months = PolicyCalculator.calculate_policy_term(start_date, end_date)
            premium = PolicyCalculator.calculate_premium(
                PolicyType[policy_type],
                coverage_amount,
                term_months,
                {"base_score": risk_score.base_score}  # Example risk_factors dict
            )
            policy.set_premium(premium)

            if self.customer.add_policy(policy):
                self.policy_manager.add_policy(policy)  # Ensure PolicyManager also adds the policy
                print(f"\nPolicy {policy_id} created successfully!")
                print(f"Calculated Premium: ${premium:,.2f}")

                # Save policy immediately
                self.save_data()
            else:
                print("Failed to create policy.")
        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"Error creating policy: {str(e)}")

    def file_claim(self):
        self.view_policies()
        if not self.customer.policies:
            print("No policies available for claims.")
            return

        policy_id = input("\nEnter Policy ID for claim: ").strip()
        
        try:
            amount = float(input("Enter claim amount: $"))
            if amount <= 0:
                print("Claim amount must be positive.")
                return

            description = input("Enter claim description: ")
            
            # Generate unique claim ID
            claim_id = self._generate_claim_id()
            
            claim = Claim(
                claim_id=claim_id,
                policy_id=policy_id,
                customer_id=self.customer.email
            )
            claim.set_amount(amount)
            claim.set_description(description)
            
            if self.customer.add_claim(claim):
                print(f"Claim {claim_id} filed successfully!")
            else:
                print("Failed to file claim. Please ensure policy is active.")

        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"Error filing claim: {str(e)}")

    # ... (keep other existing methods)
    def display_menu(self):
        print("\n=== Customer Policy Management System ===")
        print("1. View My Profile")
        print("2. View My Policies")
        print("3. Request New Policy")
        print("4. File a Claim")
        print("5. View My Claims")
        print("6. Update Contact Information")
        print("7. Save Data")
        print("8. Load Data")
        print("9. Exit")

    def run(self):
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-9): ").strip()

            if choice == "1":
                self.view_profile()
            elif choice == "2":
                self.view_policies()
            elif choice == "3":
                self.request_new_policy()
            elif choice == "4":
                self.file_claim()
            elif choice == "5":
                self.view_claims()
            elif choice == "6":
                self.update_contact_info()
            elif choice == "7":
                self.save_data()
            elif choice == "8":
                self.load_data()
            elif choice == "9":
                print("Thank you for using the Policy Management System!")
                break
            else:
                print("Invalid choice. Please try again.")

    def view_profile(self):
        print("\n=== My Profile ===")
        print(self.customer)
        print(f"Total Coverage: ${self.customer.calculate_total_coverage():,.2f}")
        print(f"Total Premium: ${self.customer.calculate_total_premium():,.2f}")

    def view_policies(self):
        policies = self.customer.get_policies()
        if not policies:
            print("\nNo policies found.")
            return

        print("\n=== My Policies ===")
        for policy in policies:
            print(f"\nPolicy ID: {policy['policy_id']}")
            
            # Handle policy type display
            policy_type = policy['policy_type']
            if isinstance(policy_type, (int, str)) and policy_type.isdigit():
                # If it's a number, convert to policy name
                try:
                    policy_type = PolicyType(int(policy_type)).name
                except ValueError:
                    pass
            print(f"Type: {policy_type}")
            
            print(f"Status: {policy['status']}")
            print(f"Coverage: ${float(policy['coverage_amount']):,.2f}")
            print(f"Premium: ${float(policy['premium']):,.2f}")
            
            # Display policy-specific details
            if policy_type == 'CAR':
                print(f"Vehicle Model: {policy.get('vehicle_model', 'N/A')}")
                print(f"Vehicle Condition: {policy.get('vehicle_condition', 'N/A')}")
            elif policy_type == 'LIFE':
                print(f"Beneficiary: {policy.get('beneficiary', 'N/A')}")
            elif policy_type == 'HEALTH':
                print(f"Includes Dental: {'Yes' if policy.get('includes_dental') else 'No'}")
                if 'deductible' in policy:
                    print(f"Deductible: ${float(policy['deductible']):,.2f}")
            elif policy_type == 'PROPERTY':
                print(f"Property Address: {policy.get('property_address', 'N/A')}")
                print(f"Property Type: {policy.get('property_type', 'N/A')}")
                
    def view_claims(self):
        claims = self.customer.get_claims()
        if not claims:
            print("\nNo claims found.")
            return

        print("\n=== My Claims ===")
        for claim in claims:
            print(f"\nClaim ID: {claim['claim_id']}")
            print(f"Policy ID: {claim['policy_id']}")
            print(f"Amount: ${claim['amount']:,.2f}")
            print(f"Status: {claim['status']}")
            print(f"Description: {claim['description']}")

    def update_contact_info(self):
        print("\n=== Update Contact Information ===")
        contact_number = input("Enter new contact number (or press Enter to skip): ").strip()
        address = input("Enter new address (or press Enter to skip): ").strip()
        
        if self.customer.update_contact_info(
            contact_number=contact_number if contact_number else None,
            address=address if address else None
        ):
            print("Contact information updated successfully!")
        else:
            print("Failed to update contact information.")
    def save_data(self):
        if DataStorageService.save_customer_data(self.customer):
            print("Data saved successfully!")
        else:
            print("Failed to save data.")

    def load_data(self):
        customer_data = DataStorageService.load_customer_data(self.customer.email)
        if customer_data:
            loaded_customer = Customer.from_dict(customer_data)
            if loaded_customer:
                self.customer = loaded_customer
                self._update_counters()  # Make sure counters are updated based on loaded data
                print("Data loaded successfully!")
            else:
                print("Failed to parse customer data.")
        else:
            print("Failed to load data.")

# Example Usage
if __name__ == "__main__":
    # Create a customer
    customer = Customer(
        email="johndoe@example.com",
        name="John Doe",
        password="password123",
        contact_number="1234567890",
        address="123 Main Street",
        birth_date=datetime(1990, 1, 1),
        credit_score=750.0
    )

    # Create and add life policy
    life_policy = LifePolicy(policy_id="POL123", customer_id="johndoe@example.com")
    life_policy.set_coverage_amount(100000.0)
    premium = PolicyCalculator.calculate_premium(
        policy_type=PolicyType.LIFE,
        coverage_amount=life_policy.get_coverage_amount(),
        term_months=12,
        risk_factors={"age": 30}
    )
    life_policy.set_premium(premium)
    customer.add_policy(life_policy)

    # Create and add car policy
    car_policy = CarPolicy(policy_id="POL124", customer_id="johndoe@example.com")
    car_policy.set_coverage_amount(50000.0)
    premium = PolicyCalculator.calculate_premium(
        policy_type=PolicyType.CAR,
        coverage_amount=car_policy.get_coverage_amount(),
        term_months=12,
        risk_factors={"age": 30}
    )
    car_policy.set_premium(premium)
    customer.add_policy(car_policy)
  
    # Display policy choices
    customer.display_policy_choices()

    # Approve a policy
    if customer.approve_policy("POL123", PolicyStatus.APPROVED):
        print("Policy POL123 approved successfully.")
    else:
        print("Failed to approve policy POL123.")

    # Create and add claims
    claim1 = Claim(claim_id="CLM001", policy_id="POL123", customer_id="johndoe@example.com")
    claim1.set_amount(5000.0)
    claim1.set_description("Hospitalization due to accident")
    claim1.add_evidence("evidence1.jpg")
    customer.add_claim(claim1)

    claim2 = Claim(claim_id="CLM002", policy_id="POL124", customer_id="johndoe@example.com")
    claim2.set_amount(3000.0)
    claim2.set_description("Car damage repair")
    claim2.add_evidence("evidence2.jpg")
    customer.add_claim(claim2)

    
    # Save customer data to JSON
    if customer.save_to_json("customer_data.json"):
        print("\nSuccessfully saved customer data to JSON")

    # Load customer data from JSON
    loaded_customer = Customer.load_from_json("customer_data.json")
    if loaded_customer:
        print("\nLoaded Customer Details:")
        print(loaded_customer)
        print("\nLoaded Policies:")
        for policy in loaded_customer.get_policies():
            print(f"\nPolicy ID: {policy['policy_id']}")
            print(f"Type: {policy['policy_type']}")
            print(f"Coverage: ${float(policy['coverage_amount']):,.2f}")
            print(f"Premium: ${float(policy['premium']):,.2f}")

    
    # Print customer details
    print(customer)
    # Print policies
    print(customer.get_policies())
    # Print claims
    print(customer.get_claims())


