from tabulate import tabulate
from datetime import date
from typing import List, Dict, Optional, Tuple
from auth import AuthenticationManager


class User:
    def __init__(self, email: str, name: str = "", password: str = "", access_level: str = "user"):
        self.email = email
        self.name = name
        self.password = password
        self.access_level = access_level
        self.address: str = ""
        self.customer_type: str = ""
        self.registration_date: date = date.today()
        self.credit_score: float = 0.0
        self._contact_number: str = ""

    def get_address(self) -> str:
        return self.address

    def get_customer_type(self) -> str:
        return self.customer_type

    def get_credit_score(self) -> float:
        return self.credit_score

    def get_contact_number(self) -> str:
        return self._contact_number

    def set_address(self, address: str) -> bool:
        try:
            self.address = address
            return True
        except:
            return False

    def set_customer_type(self, type: str) -> bool:
        try:
            self.customer_type = type
            return True
        except:
            return False

    def set_credit_score(self, score: float) -> bool:
        try:
            self.credit_score = score
            return True
        except:
            return False

    def set_contact_number(self, number: str) -> bool:
        try:
            self._contact_number = number
            return True
        except:
            return False


class UserManager:
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.users: Dict[str, User] = {}  # email -> User

    def create_user(self, email: str, password: str) -> Tuple[bool, str]:
        """Create or retrieve a user profile"""
        try:
            # Check if user exists in auth system
            if email not in self.auth_manager._users:
                # If not in auth system, try to register
                success, message = self.auth_manager.register(email, password, role='customer')
                if not success:
                    return False, message

            # Create user profile if it doesn't exist
            if email not in self.users:
                user = User(email)
                self.users[email] = user
                return True, "User profile created successfully"

            return True, "User profile already exists"

        except Exception as e:
            return False, f"Error creating user profile: {str(e)}"

    def get_user(self, email: str) -> Optional[User]:
        return self.users.get(email)

    def update_user(self, email: str, **kwargs) -> Tuple[bool, str]:
        user = self.get_user(email)
        if not user:
            return False, "User not found"

        try:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return True, "User updated successfully"
        except Exception as e:
            return False, f"Update failed: {str(e)}"

    def lookup_customer(self, customer_id: str) -> Optional[Dict]:
        """Look up customer details - accessible by all roles"""
        user = self.get_user(customer_id)
        if user:
            return {
                "customer_id": user.email,
                "name": getattr(user, 'name', ''),
                "contact": user.get_contact_number(),
                "address": user.get_address(),
                "credit_score": user.get_credit_score(),
                "registration_date": user.registration_date
            }
        return None


class UserCLI:
    def __init__(self, auth_manager: AuthenticationManager):
        self.user_manager = UserManager(auth_manager)
        self.current_user = None

    def display_menu(self):
        print("\n=== User Management ===")
        menu_options = [
            ["1", "Create New User"],
            ["2", "Update User Profile"],
            ["3", "View User Profile"],
            ["4", "Back to Main Menu"]
        ]
        print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="grid"))

    def create_user(self):
        print("\n=== Create New User ===")
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()

        success, message = self.user_manager.create_user(email, password)
        print(message)

        if success:
            user = self.user_manager.get_user(email)
            self._update_user_details(user)

    def _update_user_details(self, user: User):
        print("\nEnter user details:")
        address = input("Address: ").strip()
        customer_type = input("Customer type: ").strip()
        contact_number = input("Contact number: ").strip()

        try:
            credit_score = float(input("Credit score: ").strip())
        except ValueError:
            credit_score = 0.0

        self.user_manager.update_user(
            user.email,
            address=address,
            customer_type=customer_type,
            credit_score=credit_score,
            _contact_number=contact_number
        )

    def update_profile(self):
        if not self.current_user:
            print("Please login first!")
            return

        print("\n=== Update Profile ===")
        self._update_user_details(self.current_user)

    def view_profile(self):
        if not self.current_user:
            print("Please login first!")
            return

        user = self.user_manager.get_user(self.current_user.email)
        if user:
            print("\n=== User Profile ===")
            print(f"Email: {user.email}")
            print(f"Address: {user.address}")
            print(f"Customer Type: {user.customer_type}")
            print(f"Registration Date: {user.registration_date}")
            print(f"Credit Score: {user.credit_score}")
            print(f"Contact Number: {user.get_contact_number()}")
        else:
            print("User profile not found!")

    def run(self):
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                self.create_user()
            elif choice == "2":
                self.update_profile()
            elif choice == "3":
                self.view_profile()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")
