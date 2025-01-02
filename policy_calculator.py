#policy_calculator.py
from typing import Dict
from datetime import datetime
from auth import AuthenticationManager
from policy_enums import PolicyType, PolicyStatus
from claim import Claim
from payment import Payment

class RiskScore:
    def __init__(self, base_score: float, confidence: float = 0.95):
        self.base_score = base_score
        self.confidence = confidence
        self.factors = {}

    def add_factor(self, name: str, value: float):
        self.factors[name] = value

class PolicyCalculator:
    """Static class for policy-related calculations"""

    BASE_RATES = {
        PolicyType.LIFE: 0.005,    # 0.5% of coverage per year
        PolicyType.CAR: 0.04,      # 4% of coverage per year
        PolicyType.HEALTH: 0.06,   # 6% of coverage per year
        PolicyType.PROPERTY: 0.02  # 2% of coverage per year
    }

    RISK_FACTOR_MAPPINGS = {
        "driving_history": {
            "CLEAN": 1.0,
            "MINOR_VIOLATIONS": 1.2,
            "MAJOR_VIOLATIONS": 1.5
        },
        "parking_location": {
            "GARAGE": 1.0,
            "STREET": 1.2,
            "PUBLIC": 1.3
        },
        "vehicle_condition": {
            "EXCELLENT": 1.0,
            "GOOD": 1.1,
            "FAIR": 1.2,
            "POOR": 1.3
        }
    }

    @staticmethod
    def calculate_premium(policy_type: PolicyType, coverage_amount: float, term_months: int, risk_factors: Dict) -> float:
        """Calculate premium based on policy type, coverage, term and risk factors"""
        if coverage_amount <= 0 or term_months <= 0:
            raise ValueError("Coverage amount and term must be positive numbers.")
    
        # Get base rate for policy type
        base_rate = PolicyCalculator.BASE_RATES.get(policy_type, 0.03)
    
        # Calculate base premium (annualized)
        base_premium = coverage_amount * base_rate
    
        # Adjust for policy term
        term_years = term_months / 12
        term_adjusted_premium = base_premium * term_years
    
        # Apply risk factor adjustments
        if risk_factors:
            multiplier = PolicyCalculator._calculate_risk_multiplier(policy_type, risk_factors)
            term_adjusted_premium *= multiplier
    
        return round(term_adjusted_premium, 2)

    @staticmethod
    def _calculate_risk_multiplier(policy_type: PolicyType, risk_factors: Dict) -> float:
        """Calculate risk multiplier based on policy type and risk factors"""
        multiplier = 1.0
    
        if policy_type == PolicyType.CAR:
            driver_age = risk_factors.get("age", 30)
            base_score = risk_factors.get("base_score", 1.0)
            multiplier += base_score  # Simple example adjustment
    
        elif policy_type == PolicyType.LIFE:
            age = risk_factors.get("age", 30)
            multiplier += 0.01 * age  # Example adjustment based on age
    
        elif policy_type == PolicyType.HEALTH:
            health_score = risk_factors.get("health_score", 0.5)
            multiplier += health_score  # Example adjustment based on health
    
        elif policy_type == PolicyType.PROPERTY:
            location_risk = risk_factors.get("location_risk", 0.5)
            multiplier += location_risk  # Example adjustment based on location risk
    
        return multiplier

    @staticmethod
    def calculate_car_risk_score(driver_age: int, vehicle_score: float, accident_history: list, location_risk: float) -> RiskScore:
        """Calculate risk score for car insurance"""
        base_score = 0.0
        
        # Age factor
        if (driver_age < 25 or driver_age > 70):
            base_score += 0.3
        elif (driver_age < 30 or driver_age > 60):
            base_score += 0.2
        
        # Vehicle factor
        base_score += vehicle_score
        
        # Accident history
        base_score += len(accident_history) * 0.2
        
        # Location risk
        base_score += location_risk
        
        # Normalize score
        base_score = min(1.0, base_score)
        
        risk_score = RiskScore(base_score)
        risk_score.add_factor("age", driver_age)
        risk_score.add_factor("vehicle", vehicle_score)
        risk_score.add_factor("accidents", len(accident_history))
        risk_score.add_factor("location", location_risk)
        
        return risk_score

    @staticmethod
    def calculate_health_risk_score(age: int, medical_history: dict, lifestyle_score: float, occupation_risk: float) -> RiskScore:
        """Calculate risk score for health insurance"""
        base_score = 0.0
        
        # Age factor
        base_score += age * 0.01  # 1% per year
        
        # Medical history
        base_score += medical_history.get("current_health", 0.5)
        
        # Lifestyle
        base_score += lifestyle_score
        
        # Occupation
        base_score += occupation_risk
        
        # Normalize score
        base_score = min(1.0, base_score / 4)
        
        risk_score = RiskScore(base_score)
        risk_score.add_factor("age", age * 0.01)
        risk_score.add_factor("medical", medical_history.get("current_health", 0.5))
        risk_score.add_factor("lifestyle", lifestyle_score)
        risk_score.add_factor("occupation", occupation_risk)
        
        return risk_score

    @staticmethod
    def calculate_property_risk_score(location_data: dict, property_details: dict, security_score: float, building_age: int) -> RiskScore:
        """Calculate risk score for property insurance"""
        base_score = 0.0
        
        # Location factors
        base_score += location_data.get("natural_disaster", 0.0)
        base_score += location_data.get("crime_rate", 0.0)
        
        # Building factors
        base_score += min(1.0, building_age * 0.02)  # 2% per year up to 100%
        
        # Security
        base_score -= security_score  # Better security reduces risk
        
        # Property condition
        condition_score = (property_details.get("construction_quality", 0.5) +
                          property_details.get("maintenance", 0.5) +
                          property_details.get("utilities_condition", 0.5)) / 3
        base_score += condition_score
        
        # Normalize score
        base_score = max(0.0, min(1.0, base_score))
        
        risk_score = RiskScore(base_score)
        risk_score.add_factor("location", (location_data.get("natural_disaster", 0) + 
                                         location_data.get("crime_rate", 0)) / 2)
        risk_score.add_factor("age", min(1.0, building_age * 0.02))
        risk_score.add_factor("security", security_score)
        risk_score.add_factor("condition", condition_score)
        
        return risk_score

    @staticmethod
    def calculate_life_risk_score(age: int, health_score: float, lifestyle_factors: dict, family_history: list) -> RiskScore:
        """
        Calculate risk score for life insurance based on various factors.
        Returns a RiskScore object with detailed risk assessment.
        """
        # Base risk calculation
        age_factor = 0.01 * age  # 1% risk per year
        health_factor = health_score
        lifestyle_risk = sum(lifestyle_factors.values())
        family_risk = 0.1 * len(family_history)  # 10% per family history item

        # Calculate base score (normalized between 0 and 1)
        base_score = min(1.0, (age_factor + health_factor + lifestyle_risk + family_risk) / 4)
        
        # Create RiskScore object
        risk_score = RiskScore(base_score)
        
        # Add individual factors for detailed assessment
        risk_score.add_factor("age", age_factor)
        risk_score.add_factor("health", health_factor)
        risk_score.add_factor("lifestyle", lifestyle_risk)
        risk_score.add_factor("family_history", family_risk)
        
        # Adjust confidence based on provided information
        confidence = 0.95  # Base confidence
        if not lifestyle_factors:
            confidence *= 0.9  # Reduce confidence if lifestyle info missing
        if not family_history:
            confidence *= 0.95  # Slight reduction if no family history provided
            
        risk_score.confidence = confidence
        
        return risk_score

    @staticmethod
    def calculate_policy_term(start_date: datetime, end_date: datetime) -> int:
        """Calculate policy term in months"""
        if not start_date or not end_date or end_date <= start_date:
            return 0

        months = (end_date.year - start_date.year) * 12
        months += end_date.month - start_date.month

        if end_date.day < start_date.day:
            months -= 1

        return max(months, 1)  # Minimum 1 month
