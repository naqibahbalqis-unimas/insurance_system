from tabulate import tabulate
from auth import AuthenticationManager, AuthCLI, UserRole
from admin import Admin, AdminCLI
from users import UserManager, UserCLI
from claim_adjuster import ClaimAdjusterCLI
from underwriter import UnderwriterCLI
from agent import AgentCLI
from customer import CustomerCLI, Customer
from policy_json_handler import PolicyJSONHandler
from agent import Agent  # Add this import at the top of the file
from claim_adjuster import ClaimAdjuster  # Add this import at the top of the file




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
        self.customer_cli = None  # Initialize customer_cli

    def display_menu(self):
        print("\n=== Insurance Management System ===")
        print(f"Logged in as: {self.current_user}\n")
        user_role = self.auth_cli.auth_manager._users[self.current_user].role
        
        # Convert role number to UserRole enum if it's a number
        if isinstance(user_role, int):
            user_role = UserRole(user_role)
        elif isinstance(user_role, str):
            # Map string role to enum
            role_map = {
                'admin': UserRole.ADMIN,
                'customer': UserRole.CUSTOMER,
                'claim adjuster': UserRole.CLAIM_ADJUSTER,
                'agent': UserRole.AGENT,
                'underwriter': UserRole.UNDERWRITER
            }
            user_role = role_map.get(user_role.lower(), UserRole.CUSTOMER)
        
        menu_options = []

        # Compare using the enum
        if user_role == UserRole.ADMIN:
            menu_options = [
                ["1", "Verify Claim"],
                ["2", "Manage Policy"],
                ["3", "Generate Report"],
                ["4", "Audit User Actions"],
                ["5", "User Authentication Management"],
                ["6", "Logout"],
                ["7", "Exit"]
            ]
        elif user_role == UserRole.CLAIM_ADJUSTER:
            menu_options = [
                ["1", "Claim Adjuster Management"],
                ["2", "Logout"],
                ["3", "Exit"]
            ]
        elif user_role == UserRole.UNDERWRITER:
            menu_options = [
                ["1", "Underwriter Management"],
                ["2", "Logout"],
                ["3", "Exit"]
            ]
        elif user_role == UserRole.AGENT:
            menu_options = [
                ["1", "Agent Management"],
                ["2", "Logout"],
                ["3", "Exit"]
            ]
        else:  # CUSTOMER or unknown role
            menu_options = [
                ["1", "Customer Portal"],
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
                    
                    # Get user role after successful login
                    user_data = self.auth_cli.auth_manager._users[self.current_user]
                    user_role = user_data.role
                    
                    # Convert role number to UserRole enum if needed
                    if isinstance(user_role, int):
                        user_role = UserRole(user_role)
                    elif isinstance(user_role, str):
                        role_map = {
                            'admin': UserRole.ADMIN,
                            'customer': UserRole.CUSTOMER,
                            'claim adjuster': UserRole.CLAIM_ADJUSTER,
                            'agent': UserRole.AGENT,
                            'underwriter': UserRole.UNDERWRITER
                        }
                        user_role = role_map.get(user_role.lower(), UserRole.CUSTOMER)

                    # Initialize admin if user is admin
                    if user_role == UserRole.ADMIN:
                        admin = Admin(
                            user_id=self.current_user,
                            name=user_data.name or self.current_user.split('@')[0],
                            email=self.current_user,
                            password=user_data.password
                        )
                        self.admin_cli.current_user = admin
                    
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

            # Convert role number to UserRole enum if it's a number
            if isinstance(user_role, int):
                user_role = UserRole(user_role)
            elif isinstance(user_role, str):
                # Map string role to enum
                role_map = {
                    'admin': UserRole.ADMIN,
                    'customer': UserRole.CUSTOMER,
                    'claim adjuster': UserRole.CLAIM_ADJUSTER,
                    'agent': UserRole.AGENT,
                    'underwriter': UserRole.UNDERWRITER
                }
                user_role = role_map.get(user_role.lower(), UserRole.CUSTOMER)
                

            if user_role == UserRole.CUSTOMER:
                if choice == "1":
                    if not self.customer_cli:
                        # Try to load existing customer data first
                        loaded_customer = PolicyJSONHandler.load_policies_from_json(self.current_user)
                        if loaded_customer:
                            self.current_customer = loaded_customer
                            self.customer_cli = CustomerCLI(loaded_customer, self.current_user)
                        else:
                            # If no existing data, create new customer
                            user_data = self.auth_cli.auth_manager._users[self.current_user]
                            if not self.user_manager.get_user(self.current_user):
                                success, message = self.user_manager.create_user(
                                    self.current_user, 
                                    user_data.password,
                                    role="customer"
                                )
                                if not success:
                                    print(f"Failed to create user profile: {message}")
                                    continue
                            
                            user = self.user_manager.get_user(self.current_user)
                            if user:
                                customer = Customer(
                                    email=self.current_user,
                                    name=user_data.name or self.current_user.split('@')[0],
                                    password=user_data.password
                                )
                                self.current_customer = customer
                                self.customer_cli = CustomerCLI(customer, self.current_user)
                            else:
                                print("Customer profile not found!")
                                continue
                    self.customer_cli.run()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == UserRole.ADMIN:
                if choice == "1":
                    # Get user data from auth manager
                    user_data = self.auth_cli.auth_manager._users[self.current_user]
                    
                    # Create Admin instance with all required parameters
                    admin = Admin(
                        user_id=self.current_user,
                        name=user_data.name or self.current_user.split('@')[0],
                        email=self.current_user,
                        password=user_data.password
                    )
                    
                    # Set the admin as current user
                    self.admin_cli.current_user = admin
                    
                    self.admin_cli.admin_menu()
                elif choice == "2":
                    policy_id = input("Enter policy ID: ").strip()
                    self.admin_cli.manage_policy(policy_id)
                elif choice == "3":
                    self.admin_cli.generate_report()
                elif choice == "4":
                    user_id = input("Enter user ID: ").strip()
                    self.admin_cli.audit_user_actions(user_id)
                elif choice == "5":
                    self.admin_cli.manage_authentication()
                elif choice == "6":
                    self.logout()
                elif choice == "7":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == UserRole.CLAIM_ADJUSTER:
                if choice == "1":
                    # Get user data from auth manager
                    user_data = self.auth_cli.auth_manager._users[self.current_user]
                    
                    # Create ClaimAdjuster instance with corrected parameters
                    adjuster = ClaimAdjuster(
                        email=self.current_user,
                        name=user_data.name or self.current_user.split('@')[0],
                        password=user_data.password
                    )
                    
                    # Set the adjuster as current user
                    self.claim_adjuster_cli.current_user = adjuster
                    
                    # Now run the claim adjuster CLI
                    self.claim_adjuster_cli.run()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == UserRole.UNDERWRITER:
                if choice == "1":
                    # Get user data from auth manager
                    user_data = self.auth_cli.auth_manager._users[self.current_user]
                    
                    # Set the current user for underwriter_cli
                    self.underwriter_cli.current_user = self.current_user
                    
                    # Now run the underwriter CLI
                    self.underwriter_cli.run()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    print("Thank you for using the Policy Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            elif user_role == UserRole.AGENT:
                if choice == "1":
                    # Get user data from auth manager
                    user_data = self.auth_cli.auth_manager._users[self.current_user]
                    
                    agent = Agent(
                        user_id=self.current_user,
                        name=user_data.name or self.current_user.split('@')[0],
                        email=self.current_user,
                        password=user_data.password
                    )
                    
                    # Set the agent as current user
                    self.agent_cli.current_user = agent
                    
                    # Now run the agent CLI
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
        self.customer_cli = None  # Reset customer_cli
        print("Logged out successfully.")


if __name__ == "__main__":
    system = MainSystem()
    system.run()
