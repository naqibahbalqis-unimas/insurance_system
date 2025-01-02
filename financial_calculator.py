# financial_calculator.py
from datetime import date
from typing import List, Dict


class FinancialCalculator:
    @staticmethod
    def calculate_premium(policy_type: str, coverage_amount: float, risk_factors: Dict[str, float]) -> float:
        """Calculate insurance premium based on policy type, coverage amount and risk factors"""
        base_premium = coverage_amount * 0.1  # Basic rate of 10%

        policy_multipliers = {
            "LIFE": 1.5,
            "CAR": 1.2,
            "HEALTH": 1.3,
            "PROPERTY": 1.1
        }

        multiplier = policy_multipliers.get(policy_type, 1.0)
        premium = base_premium * multiplier

        # Apply risk factor adjustments
        for factor, value in risk_factors.items():
            premium *= (1 + value)

        return round(premium, 2)

    @staticmethod
    def calculate_claim_payout(claim_amount: float, coverage_amount: float, deductible: float) -> float:
        """Calculate claim payout considering coverage limits and deductibles"""
        if claim_amount <= deductible:
            return 0.0

        payout = min(claim_amount - deductible, coverage_amount)
        return round(payout, 2)

    @staticmethod
    def validate_payment_amount(payment_amount: float, claim_amount: float) -> bool:
        """Validate if payment amount matches approved claim amount"""
        return abs(payment_amount - claim_amount) < 0.01

    @staticmethod
    def calculate_refund_amount(payment_amount: float, processing_fee: float = 25.0) -> float:
        """Calculate refund amount considering processing fees"""
        refund = payment_amount - processing_fee
        return max(0, round(refund, 2))
