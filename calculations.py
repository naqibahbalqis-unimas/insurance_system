import datetime
import typing
from policy_enums import PolicyType, PolicyStatus
from typing import Dict
from typing import Dict, List
from policy import Policy, LifePolicy, CarPolicy, HealthPolicy, PropertyPolicy, PolicyManager
from policy_enums import PolicyType

class PolicyCalculator:
   
    
    """Static class for policy-related calculations"""

    BASE_RATES = {
        PolicyType.LIFE: 0.005,    # 0.5% of coverage per year
        PolicyType.CAR: 0.04,      # 4% of coverage per year
        PolicyType.HEALTH: 0.06,   # 6% of coverage per year
        PolicyType.PROPERTY: 0.02  # 2% of coverage per year
    }

    DRIVING_HISTORY_MULTIPLIERS = {
        "CLEAN": 1.0,
        "MINOR_VIOLATIONS": 1.2,
        "MAJOR_VIOLATIONS": 1.5,
        "ACCIDENTS": 1.8
    }

    PARKING_LOCATION_MULTIPLIERS = {
        "GARAGE": 1.0,
        "DRIVEWAY": 1.1,
        "STREET": 1.3,
        "PUBLIC_PARKING": 1.4
    }

    
    @staticmethod
    def calculate_premium(policy_type: PolicyType, coverage_amount: float, term_months: int, risk_factors: Dict) -> float:
        """
        Calculate policy premium based on type, coverage amount, term and risk factors
        :param policy_type: Type of policy (LIFE, CAR, etc.)
        :param coverage_amount: Amount of coverage
        :param term_months: Term in months
        :param risk_factors: Dictionary of risk factors specific to policy type
        :return: Calculated premium amount
        """
        if coverage_amount <= 0 or term_months <= 0:
            return 0.0

        # Get base rate for policy type
        base_rate = PolicyCalculator.BASE_RATES.get(policy_type, 0.03)  # Default 3%
        
        # Calculate base premium (annualized)
        base_premium = coverage_amount * base_rate

        # Adjust for policy term
        term_years = term_months / 12
        term_adjusted_premium = base_premium * term_years

        # Apply risk factor adjustments
        if risk_factors:
            risk_multiplier = PolicyCalculator._calculate_risk_multiplier(policy_type, risk_factors)
            term_adjusted_premium *= risk_multiplier

        return round(term_adjusted_premium, 2)

    @staticmethod
    def _calculate_risk_multiplier(policy_type: PolicyType, risk_factors: Dict) -> float:
        """Calculate risk multiplier based on policy type and risk factors"""
        multiplier = 1.0

        if policy_type == PolicyType.CAR:
            # Numeric factors
            vehicle_age = float(risk_factors.get('vehicle_age', 0))
            annual_mileage = float(risk_factors.get('annual_mileage', 12000))
            
            # Age-based multiplier
            if vehicle_age > 10:
                multiplier *= 1.4
            elif vehicle_age > 5:
                multiplier *= 1.2
                
            # Mileage-based multiplier
            if annual_mileage > 20000:
                multiplier *= 1.3
            elif annual_mileage > 15000:
                multiplier *= 1.2
                
            # String-based factors with lookup tables
            driving_history = risk_factors.get('driving_history', 'CLEAN').upper()
            multiplier *= PolicyCalculator.DRIVING_HISTORY_MULTIPLIERS.get(driving_history, 1.0)
            
            parking_location = risk_factors.get('parking_location', 'GARAGE').upper()
            multiplier *= PolicyCalculator.PARKING_LOCATION_MULTIPLIERS.get(parking_location, 1.0)

        elif policy_type == PolicyType.LIFE:
            age = float(risk_factors.get('age', 30))
            if age > 60:
                multiplier *= 1.5
            elif age > 40:
                multiplier *= 1.2

        elif policy_type == PolicyType.HEALTH:
            pre_conditions = float(risk_factors.get('pre_conditions', 0))
            multiplier *= (1 + (0.1 * pre_conditions))

        elif policy_type == PolicyType.PROPERTY:
            location_risk = risk_factors.get('location_risk', 'LOW')
            risk_values = {'LOW': 1.0, 'MEDIUM': 1.3, 'HIGH': 1.6}
            multiplier *= risk_values.get(location_risk.upper(), 1.0)

        return multiplier



    @staticmethod
    def calculate_policy_term(start_date: datetime, end_date: datetime) -> int:
        """Calculate policy term in months"""
        if not start_date or not end_date or end_date <= start_date:
            return 0
        
        months = (end_date.year - start_date.year) * 12
        months += end_date.month - start_date.month
        
        # Adjust for day of month if needed
        if end_date.day < start_date.day:
            months -= 1
            
        return max(months, 1)  # Minimum 1 month