# payment.py
from datetime import date
from typing import Dict

class Payment:
    def __init__(self, payment_id: str, policy_id: str):
        self.payment_id: str = payment_id
        self.policy_id: str = policy_id
        self.amount: float = 0.0
        self.payment_date: date = date.today()
        self.payment_status: str = "PENDING"
        self.payment_method: str = ""
        self.transaction_id: str = ""

    def get_payment_id(self) -> str:
        return self.payment_id

    def get_amount(self) -> float:
        return self.amount

    def get_status(self) -> str:
        return self.payment_status

    def get_payment_method(self) -> str:
        return self.payment_method

    def set_amount(self, amount: float) -> bool:
        if amount > 0:
            self.amount = amount
            return True
        return False

    def set_status(self, status: str) -> bool:
        valid_statuses = ["PENDING", "COMPLETED", "FAILED"]
        if status in valid_statuses:
            self.payment_status = status
            return True
        return False

    def set_payment_method(self, method: str) -> bool:
        valid_methods = ["BANK_TRANSFER", "CREDIT_CARD", "CHECK"]
        if method in valid_methods:
            self.payment_method = method
            return True
        return False

    def process_payment(self) -> bool:
        if all([
            self.payment_id,
            self.policy_id,
            self.amount > 0,
            self.payment_method
        ]):
            self.payment_status = "COMPLETED"
            self.transaction_id = f"TXN_{self.payment_id}"
            return True
        return False

    def generate_receipt(self) -> Dict:
        return {
            "payment_id": self.payment_id,
            "amount": self.amount,
            "date": self.payment_date,
            "status": self.payment_status,
            "method": self.payment_method,
            "transaction_id": self.transaction_id
        }

    def refund_payment(self) -> bool:
        if self.payment_status == "COMPLETED":
            self.payment_status = "REFUNDED"
            return True
        return False

    def verify_payment(self) -> bool:
        # Add payment verification logic here
        return all([
            self.payment_id,
            self.policy_id,
            self.amount > 0,
            self.payment_method,
            self.transaction_id
        ])

    def get_transaction_details(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "payment_id": self.payment_id,
            "amount": self.amount,
            "date": self.payment_date,
            "status": self.payment_status,
            "method": self.payment_method
        }
