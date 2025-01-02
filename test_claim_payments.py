# test_claim_payments.py
import unittest
from datetime import date
from claim import Claim
from payment import Payment
from financial_calculator import FinancialCalculator


class TestClaimPayments(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.claim = Claim("CL001", "POL001", "CUST001")
        self.payment = Payment("PAY001", "POL001")
        self.calculator = FinancialCalculator()

    def test_claim_initialization(self):
        """Test claim initialization and getters"""
        self.assertEqual(self.claim.get_claim_id(), "CL001")
        self.assertEqual(self.claim.get_status(), "PENDING")
        self.assertEqual(self.claim.get_amount(), 0.0)
        self.assertEqual(self.claim.get_description(), "")

    def test_claim_setters(self):
        """Test claim setter methods"""
        self.assertTrue(self.claim.set_amount(1000.0))
        self.assertEqual(self.claim.get_amount(), 1000.0)

        self.assertTrue(self.claim.set_status("APPROVED"))
        self.assertEqual(self.claim.get_status(), "APPROVED")

        self.assertTrue(self.claim.set_description("Test claim"))
        self.assertEqual(self.claim.get_description(), "Test claim")

    def test_invalid_claim_setters(self):
        """Test invalid inputs for claim setters"""
        self.assertFalse(self.claim.set_amount(-100.0))
        self.assertFalse(self.claim.set_status("INVALID"))
        self.assertFalse(self.claim.set_description(""))

    def test_claim_evidence(self):
        """Test evidence document handling"""
        self.assertTrue(self.claim.add_evidence("DOC001"))
        self.assertIn("DOC001", self.claim.evidence_documents)
        self.assertFalse(self.claim.add_evidence(""))

    def test_claim_processing(self):
        """Test claim processing workflow"""
        self.claim.set_amount(1000.0)
        self.assertTrue(self.claim.submit_claim())
        self.assertTrue(self.claim.process_claim())
        # Set status to APPROVED before calculating payout
        self.claim.set_status("APPROVED")
        self.assertEqual(self.claim.calculate_payout(), 1000.0)

    def test_payment_initialization(self):
        """Test payment initialization and getters"""
        self.assertEqual(self.payment.get_payment_id(), "PAY001")
        self.assertEqual(self.payment.get_status(), "PENDING")
        self.assertEqual(self.payment.get_amount(), 0.0)
        self.assertEqual(self.payment.get_payment_method(), "")

    def test_payment_setters(self):
        """Test payment setter methods"""
        self.assertTrue(self.payment.set_amount(1000.0))
        self.assertEqual(self.payment.get_amount(), 1000.0)

        self.assertTrue(self.payment.set_status("COMPLETED"))
        self.assertEqual(self.payment.get_status(), "COMPLETED")

        self.assertTrue(self.payment.set_payment_method("BANK_TRANSFER"))
        self.assertEqual(self.payment.get_payment_method(), "BANK_TRANSFER")

    def test_invalid_payment_setters(self):
        """Test invalid inputs for payment setters"""
        self.assertFalse(self.payment.set_amount(-100.0))
        self.assertFalse(self.payment.set_status("INVALID"))
        self.assertFalse(self.payment.set_payment_method("INVALID_METHOD"))

    def test_payment_processing(self):
        """Test payment processing workflow"""
        self.payment.set_amount(1000.0)
        self.payment.set_payment_method("CREDIT_CARD")
        self.assertTrue(self.payment.process_payment())
        self.assertEqual(self.payment.get_status(), "COMPLETED")
        self.assertTrue(self.payment.verify_payment())

    def test_payment_receipt(self):
        """Test payment receipt generation"""
        self.payment.set_amount(1000.0)
        self.payment.set_payment_method("BANK_TRANSFER")
        self.payment.process_payment()

        receipt = self.payment.generate_receipt()
        self.assertEqual(receipt["amount"], 1000.0)
        self.assertEqual(receipt["method"], "BANK_TRANSFER")
        self.assertIn("transaction_id", receipt)

    def test_payment_refund(self):
        """Test payment refund functionality"""
        self.payment.set_amount(1000.0)
        self.payment.set_payment_method("CREDIT_CARD")
        self.payment.process_payment()
        self.assertTrue(self.payment.refund_payment())
        self.assertEqual(self.payment.get_status(), "REFUNDED")

    def test_financial_calculations(self):
        """Test financial calculator methods"""
        # Test premium calculation
        premium = FinancialCalculator.calculate_premium(
            "LIFE",
            100000.0,
            {"age": 0.1, "health": 0.05}
        )
        self.assertGreater(premium, 0)

        # Test claim payout calculation
        payout = FinancialCalculator.calculate_claim_payout(5000.0, 10000.0, 500.0)
        self.assertEqual(payout, 4500.0)

        # Test payment validation
        self.assertTrue(
            FinancialCalculator.validate_payment_amount(1000.0, 1000.0)
        )

        # Test refund calculation
        refund = FinancialCalculator.calculate_refund_amount(1000.0)
        self.assertEqual(refund, 975.0)


if __name__ == '__main__':
    unittest.main()