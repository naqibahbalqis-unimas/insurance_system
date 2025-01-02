import unittest
from customer import Customer
from agent import Agent

class TestUserManagement(unittest.TestCase):

    def test_customer_details(self):
        customer = Customer("C001", "Arif", "arif@example.com", "password123", "Customer", "Unimas Samarahan", 700, 1000.00)
        self.assertEqual(customer.get_user_details(), {
            "user_id": "C001",
            "name": "Arif",
            "email": "arif@example.com",
            "address": "Unimas Samarahan",
            "credit_score": 700,
            "premium_amount": 1000.00
        })

        customer.update_user_details(name="Arif Updated", address="Unimas Kota Samarahan")
        self.assertEqual(customer.name, "Arif Updated")
        self.assertEqual(customer.address, "Unimas Kota Samarahan")

    def test_agent_details(self):
        agent = Agent("A001", "Bob", "bob@example.com", "password123", "Agent", 0.05, 50000)
        self.assertEqual(agent.get_user_details(), {
            "user_id": "A001",
            "name": "Bob",
            "email": "bob@example.com",
            "commission_rate": 0.05,
            "sales_target": 50000
        })

        agent.update_user_details(email="bob.updated@example.com", sales_target=60000)
        self.assertEqual(agent.email, "bob.updated@example.com")
        self.assertEqual(agent.sales_target, 60000)

    def test_commission_calculation(self):
        agent = Agent("A002", "Charles", "charles@example.com", "securepassword", "Agent", 0.1, 100000)
        self.assertEqual(agent.calculate_commission(50000), 5000.00)

    def test_customer_premium_calculation(self):
        customer = Customer("C002", "Shukri", "Shukri@example.com", "mypassword", "Customer", "Unimas Samarahan", 650, 1000.00)
        self.assertAlmostEqual(customer.calculate_total_premium(), 950.00)

if __name__ == "__main__":
    unittest.main()
