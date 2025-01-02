import unittest
from policy import Policy
from policy_enums import PolicyType, PolicyStatus
from policy_calculator import PolicyCalculator


class TestPolicyManagement(unittest.TestCase):
    def setUp(self):
        self.policy = Policy("POL001", "CUST001", PolicyType.HEALTH)

    def test_policy_initialization(self):
        self.assertEqual(self.policy.get_policy_id(), "POL001")
        self.assertEqual(self.policy.get_customer_id(), "CUST001")
        self.assertEqual(self.policy.get_policy_type(), PolicyType.HEALTH)
        self.assertEqual(self.policy.get_status(), PolicyStatus.ACTIVE)

    def test_policy_setters(self):
        self.assertTrue(self.policy.set_coverage_amount(100000))
        self.assertEqual(self.policy.coverage_amount, 100000)

        self.assertTrue(self.policy.set_premium(5000))
        self.assertEqual(self.policy.premium, 5000)

    def test_policy_status_update(self):
        self.assertTrue(self.policy.update_status(PolicyStatus.LAPSED))
        self.assertEqual(self.policy.get_status(), PolicyStatus.LAPSED)

    def test_policy_conditions(self):
        self.assertTrue(self.policy.add_condition("No pre-existing conditions"))
        self.assertIn("No pre-existing conditions", self.policy.conditions)

    def test_premium_calculation(self):
        premium = PolicyCalculator.calculate_premium(
            PolicyType.HEALTH, 100000, {"age": 0.1, "smoking": 0.2}
        )
        self.assertGreater(premium, 0)

    def test_policy_term_calculation(self):
        days = PolicyCalculator.calculate_policy_term("2024-01-01", "2025-01-01")
        self.assertEqual(days, 365)


if __name__ == "__main__":
    unittest.main()
