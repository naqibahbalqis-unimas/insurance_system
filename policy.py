# policy.py
from datetime import datetime
from typing import List, Dict, Optional
from policy_enums import PolicyType, PolicyStatus
from policy_calculator import PolicyCalculator
from typing import Dict, Optional
from policy_enums import PolicyType, PolicyStatus

class Policy:
    def __init__(self, policy_id: str, customer_id: str, policy_type: PolicyType):
        self.policy_id = policy_id
        self.customer_id = customer_id
        self.policy_type = policy_type
        self.policy_id: str = policy_id
        self.customer_id: str = customer_id
        self.policy_type: PolicyType = policy_type
        self.coverage_amount: float = 0.0
        self.premium: float = 0.0
        self.status: PolicyStatus = PolicyStatus.PENDING
        self.start_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None
        self.conditions: List[str] = []
        

    def get_policy_id(self) -> str:
        return self.policy_id

    def get_customer_id(self) -> str:
        return self.customer_id

    def get_policy_type(self) -> PolicyType:
        return self.policy_type

    def get_status(self) -> PolicyStatus:
        return self.status

    def get_coverage_amount(self) -> float:
        return self.coverage_amount

    def get_premium(self) -> float:
        return self.premium

    def set_coverage_amount(self, amount: float) -> bool:
        """Set coverage amount with validation"""
        if amount > 0:
            self.coverage_amount = amount
            return True
        return False

    def set_premium(self, premium: float) -> bool:
        """Set premium amount with validation"""
        if premium > 0:
            self.premium = premium
            return True
        return False

    def set_dates(self, start_date: datetime, end_date: datetime) -> bool:
        """Set policy start and end dates with validation"""
        if start_date and end_date and end_date > start_date:
            self.start_date = start_date
            self.end_date = end_date
            return True
        return False

    def update_status(self, status: PolicyStatus) -> bool:
        """Update policy status with validation"""
        if not isinstance(status, PolicyStatus):
            return False

        valid_transitions = {
            PolicyStatus.PENDING: [PolicyStatus.APPROVED, PolicyStatus.REJECTED, PolicyStatus.CANCELLED],
            PolicyStatus.APPROVED: [PolicyStatus.ACTIVE, PolicyStatus.CANCELLED],
            PolicyStatus.REJECTED: [PolicyStatus.CANCELLED],
            PolicyStatus.ACTIVE: [PolicyStatus.INACTIVE, PolicyStatus.EXPIRED, PolicyStatus.CANCELLED],
            PolicyStatus.INACTIVE: [PolicyStatus.ACTIVE, PolicyStatus.EXPIRED, PolicyStatus.CANCELLED],
            PolicyStatus.EXPIRED: [PolicyStatus.CANCELLED],
            PolicyStatus.CANCELLED: []  # Final state, no further transitions allowed
        }
        if status in valid_transitions.get(self.status, []):
            self.status = status
            return True
        return False

    def add_condition(self, condition: str) -> bool:
        """Add policy condition"""
        if condition.strip():
            self.conditions.append(condition.strip())
            return True
        return False

    def calculate_premium(self, risk_factors: Dict[str, float]) -> float:
        """Calculate premium for the policy"""
        if self.coverage_amount <= 0:
            return 0.0
            
        premium = PolicyCalculator.calculate_premium(
            self.policy_type,
            self.coverage_amount,
            PolicyCalculator.calculate_policy_term(self.start_date, self.end_date),
            risk_factors
        )
        self.premium = premium
        return premium

    def get_policy_term(self) -> int:
        """Get policy term in days"""
        if self.start_date and self.end_date:
            return PolicyCalculator.calculate_policy_term(
                self.start_date,
                self.end_date
            )
        return 0

    def validate_policy(self) -> bool:
        """Validate if policy meets all requirements"""
        return all([
            self.policy_id,
            self.customer_id,
            self.coverage_amount > 0,
            self.premium > 0,
            self.start_date and self.end_date and self.end_date > self.start_date,
            self.status != PolicyStatus.EXPIRED
        ])
        
    def to_dict(self) -> Dict:
        """Convert policy to dictionary representation"""
        return {
            'policy_id': self.policy_id,
            'customer_id': self.customer_id,
            'policy_type': self.policy_type.name,  # Use .name instead of .value
            'coverage_amount': self.coverage_amount,
            'premium': self.premium,
            'status': self.status.value,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'conditions': self.conditions
        }

class LifePolicy(Policy):
    def __init__(self, policy_id: str, customer_id: str):
        super().__init__(policy_id, customer_id, PolicyType.LIFE)
        self.beneficiary: str = ""
        self.death_benefit: float = 0.0

    def set_beneficiary(self, beneficiary: str) -> bool:
        if beneficiary.strip():
            self.beneficiary = beneficiary.strip()
            return True
        return False

    def set_death_benefit(self, amount: float) -> bool:
        if amount > 0:
            self.death_benefit = amount
            return True
        return False

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'beneficiary': self.beneficiary,
            'death_benefit': self.death_benefit
        })
        return data

class CarPolicy(Policy):
    def __init__(self, policy_id: str, customer_id: str):
        super().__init__(policy_id, customer_id, PolicyType.CAR)
        self.vehicle_id: str = ""
        self.is_comprehensive: bool = False
        self.vehicle_age: int = 0
        self.vehicle_model: str = ""
        self.vehicle_plate_number: str = ""  # Add vehicle plate number
        self.vehicle_condition: str = ""  # Add vehicle condition

    def set_vehicle_details(self, vehicle_id: str, is_comprehensive: bool, vehicle_age: int, vehicle_model: str, vehicle_plate_number: str, vehicle_condition: str) -> bool:
        if vehicle_id.strip() and vehicle_age >= 0 and vehicle_model.strip() and vehicle_plate_number.strip() and vehicle_condition.strip():
            self.vehicle_id = vehicle_id.strip()
            self.is_comprehensive = is_comprehensive
            self.vehicle_age = vehicle_age
            self.vehicle_model = vehicle_model.strip()
            self.vehicle_plate_number = vehicle_plate_number.strip()
            self.vehicle_condition = vehicle_condition.strip()
            return True
        return False

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'vehicle_id': self.vehicle_id,
            'is_comprehensive': self.is_comprehensive,
            'vehicle_age': self.vehicle_age,
            'vehicle_model': self.vehicle_model,
            'vehicle_plate_number': self.vehicle_plate_number,
            'vehicle_condition': self.vehicle_condition
        })
        return data

class HealthPolicy(Policy):
    def __init__(self, policy_id: str, customer_id: str):
        super().__init__(policy_id, customer_id, PolicyType.HEALTH)  # Make sure to pass PolicyType.HEALTH
        self.deductible: float = 0.0
        self.includes_dental: bool = False

    def set_health_details(self, deductible: float, includes_dental: bool) -> bool:
        """Set health policy specific details"""
        if deductible >= 0:
            self.deductible = deductible
            self.includes_dental = includes_dental
            return True
        return False

    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        data = super().to_dict()
        data.update({
            'deductible': self.deductible,
            'includes_dental': self.includes_dental
        })
        return data
    
class PropertyPolicy(Policy):
    def __init__(self, policy_id: str, customer_id: str):
        super().__init__(policy_id, customer_id, PolicyType.PROPERTY)
        self.property_address: str = ""
        self.property_type: str = ""

    def set_property_details(self, address: str, property_type: str) -> bool:
        if address.strip() and property_type.strip():
            self.property_address = address.strip()
            self.property_type = property_type.strip()
            return True
        return False

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'property_address': self.property_address,
            'property_type': self.property_type
        })
        return data

class PolicyManager:
    def __init__(self):
        self.policies: Dict[str, Policy] = {}

    def add_policy(self, policy: Policy) -> bool:
        if policy.policy_id not in self.policies:
            self.policies[policy.policy_id] = policy
            return True
        return False

    def get_policy(self, policy_id: str) -> Optional[Policy]:
        return self.policies.get(policy_id)

    def update_policy(self, policy_id: str, **kwargs) -> bool:
        policy = self.get_policy(policy_id)
        if not policy:
            return False
        for key, value in kwargs.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        return True

    def remove_policy(self, policy_id: str) -> bool:
        if policy_id in self.policies:
            del self.policies[policy_id]
            return True
        return False