from tabulate import tabulate
from auth import AuthenticationManager, AuthCLI
from admin import Admin, AdminCLI
from users import UserManager, UserCLI
from claim_adjuster import ClaimAdjusterCLI
from underwriter import UnderwriterCLI
from agent import AgentCLI
from customer import CustomerCLI, Customer
from policy_json_handler import PolicyJSONHandler


class MainSystem:
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.auth_cli = AuthCLI()
        self.user_manager = UserManager(self.auth_manager)
        self.auth_cli.user_manager = self.user_manager
        self.admin_cli = AdminCLI(self.auth_manager)
        self.user_cli = UserCLI(self.auth_manager)
        self.claim_adjuster_cli = ClaimAdjusterCLI(self.auth_manager)
        self.underwriter_cli = UnderwriterCLI(self.auth_manager)
        self.agent_cli = AgentCLI(self.auth_manager)
        self.current_user = None
        self.current_customer = None

    def display_menu(self):
        print("\n=== Insurance Management System ===")
        print(f"Logged in as: {self.current_user}\n")
        user_role = self.auth_cli.auth_manager._users[self.current_user].role
        menu_options = []

        if user_role == "admin":
            menu_options = [
                ["1", "User Management"],
                ["2", "Admin Management"],
                ["3", "Logout"],
                ["4", "Exit"]
            ]
        elif user_role == "claim adjuster":
            menu_options = [
                ["1", "Claim Adjuster Management"],
                ["2", "Logout"],
                ["3", "Exit"]
            ]
        elif user_role == "underwriter":
            menu_options = [
                ["1", "Underwriter Management"],
                ["2", "Logout"],
                ["3", "Exit"]
            ]
        elif user_role == "agent":
            menu_options = [
                ["1", "Agent Management"],
                ["2", "Logout"],
                ["3", "Exit"]
            ]
        elif user_role == "customer":
            menu_options = [
                ["1", "User Profile"],
                ["2", "Customer Portal"],
                ["3", "Logout"],
                ["4", "Exit"]
            ]
        else:
            menu_options = [
                ["1", "User Management"],
                ["2", "Logout"],
                ["3", "Exit"]
            ]

        print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="grid"))

    def handle_auth(self):
        while not self.auth_cli.current_user:
            print("\n=== Welcome to Insurance Management System ===")
            auth_menu = [
                ["1", "Login"],
                ["2", "Register"],
                ["3", "Exit"]
            ]
            print(tabulate(auth_menu, headers=["Option", "Description"], tablefmt="grid"))
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                if self.auth_cli.login():
                    self.current_user = self.auth_cli.current_user
                    self.user_cli.current_user = self.auth_cli.current_user
                    self.admin_cli.current_user = self.auth_cli.current_user
                    return True
            elif choice == "2":
                self.auth_cli.register()
            elif choice == "3":
                return False
            else:
                print("Invalid choice. Please try again.")
        return True

    def run(self):
        while True:
            if not self.current_user:
                if not self.handle_auth():
                    print("\nGoodbye!")
                    break
                continue

            self.display_menu()
            choice = input("\nEnter your choice: ").strip()
            user_role = self.auth_cli.auth_manager._users[self.current_user].role

            if user_role == "customer":
                if choice == "1":
                    self.user_cli.run()
                elif choice == "2":
                    user_data = self.auth_cli.auth_manager._users[self.current_user]
                    if not self.user_manager.get_user(self.current_user):
                        success, _ = self.user_manager.create_user(self.current_user, user_data.password)
                        if not success:
                            print("Failed to create user profile!")
                            continue
                    
                    user = self.user_manager.get_user(self.current_user)
                    if user:
                        customer = Customer(
                            email=user_data.email,
                            name=user_data.email.split('@')[0],
                            password=user_data.password,
                            contact_number=user.get_contact_number(),
                            address=user.get_address(),
                            credit_score=user.get_credit_score()
                        )
                        self.current_customer = customer
                        customer_cli = CustomerCLI(customer)
                        customer_cli.run()
                    else:
                        print("Customer profile not found!")
                elif choice == "3":
                    self.logout()
                elif choice == "4":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == "admin":
                if choice == "1":
                    self.user_cli.run()
                elif choice == "2":
                    self.admin_cli.run()
                elif choice == "3":
                    self.logout()
                elif choice == "4":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == "claim adjuster":
                if choice == "1":
                    self.claim_adjuster_cli.run()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == "underwriter":
                if choice == "1":
                    self.underwriter_cli.run()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == "agent":
                if choice == "1":
                    self.agent_cli.run()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            else:
                if choice == "1":
                    self.user_cli.run()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")

    def save_data(self):
        if self.current_customer:
            success = PolicyJSONHandler.save_policies_to_json(self.current_customer)
            if success:
                print("Data saved successfully!")
            else:
                print("Failed to save data.")
        else:
            print("No customer data to save.")

    def load_data(self):
        loaded_data = PolicyJSONHandler.load_policies_from_json()
        if loaded_data:
            self.current_customer = Customer.load_from_json("data/customer_data.json")
            if self.current_customer:
                print("Data loaded successfully!")
                print(f"Total Premium: ${self.current_customer.calculate_total_premium():,.2f}")
            else:
                print("Failed to load customer data.")
        else:
            print("No data found to load.")

    def logout(self):
        self.current_user = None
        self.auth_cli.logout()
        self.user_cli.current_user = None
        self.admin_cli.current_user = None
        self.claim_adjuster_cli.current_user = None
        self.underwriter_cli.current_user = None
        self.agent_cli.current_user = None
        self.current_customer = None
        print("Logged out successfully.")


if __name__ == "__main__":
    system = MainSystem()
    system.run()
