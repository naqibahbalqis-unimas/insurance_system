from tabulate import tabulate
from datetime import date
from typing import List, Dict, Optional, Any
from auth import AuthenticationManager, AuthCLI, UserCredentials, UserRole
from users import User
import json




class Admin(User):
    """
    Concrete implementation of the User class for Admins.
    """

    def __init__(self, user_id: str, name: str, email: str, password: str):
        super().__init__(user_id, name, email, password)
        self.access_level = "Admin"  # Set the access level explicitly
        self.department = None  # Add the department attribute

    def get_user_details(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "access_level": self.access_level,
            "department": self.department
        }

    def update_user_details(self, name: str = None, email: str = None, password: str = None, access_level: str = None, department: str = None):
        if name:
            self.name = name
        if email:
            self.email = email
        if password:
            self.set_password(password)
        if department:
            self.department = department
        # Access level change is restricted for Admin

    def set_department(self, department: str):
        """Method to set the department of the Admin."""
        self.department = department

    def set_access_level(self, access_level: str):
        """Method to set the access level of the Admin."""
        self.access_level = access_level

    def verify_claim(self, claim_id: str) -> bool:
        """
        Verify a claim based on the claim ID.
        """
        # Implement the logic to verify the claim
        return True




class AdminCLI:
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.admin = None
        self.current_user = None

    def create_admin_account(self):
        print("\n=== Create Admin Account ===")
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()

        # Directly instantiate the Admin object here instead of calling a non-existent create_admin method
        user_id = f"admin_{email}"  # You can generate a user ID here based on the email or any other logic
        self.admin = Admin(user_id, email, email, password)

        if self.admin:
            department = input("Enter department: ").strip()
            access_level = input("Enter access level: ").strip()

            self.admin.set_department(department)
            self.admin.set_access_level(access_level)
            print("Admin account created and configured successfully!")
        else:
            print("Failed to create admin account.")

    def login(self):
        print("\n=== Admin Login ===")
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()

        success, token = self.auth_manager.login(email, password)
        if success:
            self.current_user = email
            print("Login successful!")
        else:
            print(f"Login failed: {token}")

    def admin_menu(self):
        while True:
            print("\n=== Admin Menu ===")
            menu_options = [
                ["1", "User Authentication Management"],
                ["2", "Verify Claim"],
                ["3", "Manage Policy"],
                ["4", "Generate Report"],
                ["5", "Audit User Actions"],
                ["6", "Logout"]
            ]
            print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="grid"))

            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self.manage_authentication()
            elif choice == "2":
                claim_id = input("Enter claim ID: ").strip()
                if self.admin.verify_claim(claim_id):
                    print("Claim verified successfully!")
                else:
                    print("You do not have the privilege to verify claims.")
            elif choice == "3":
                policy_id = input("Enter policy ID: ").strip()
                if self.admin.manage_policy(policy_id):
                    print("Policy managed successfully!")
                else:
                    print("You do not have the privilege to manage policies.")
            elif choice == "4":
                report = self.admin.generate_report()
                print("\n=== Admin Report ===")
                for key, value in report.items():
                    print(f"{key}: {value}")
            elif choice == "5":
                user_id = input("Enter user ID: ").strip()
                actions = self.admin.audit_user_actions(user_id)
                if actions:
                    print("\n=== User Actions ===")
                    for action in actions:
                        print(f"- {action}")
                else:
                    print("No actions found.")
            elif choice == "6":
                print("Logging out...")
                self.current_user = None
                break
            else:
                print("Invalid choice. Please try again.")

    def manage_authentication(self):
        while True:
            print("\n=== User Authentication Management ===")
            auth_menu_options = [
                ["1", "List All Users"],
                ["2", "Change User Role"],
                ["3", "Reset User Password"],
                ["4", "Update User Details"],
                ["5", "Delete User"],
                ["6", "Back to Admin Menu"]
            ]
            print(tabulate(auth_menu_options, headers=["Option", "Description"], tablefmt="grid"))

            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self.list_all_users()
            elif choice == "2":
                self.change_user_role()
            elif choice == "3":
                self.reset_user_password()
            elif choice == "4":
                self.update_user_details()
            elif choice == "5":
                self.delete_user()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")

    def list_all_users(self):
        print("\n=== All Users ===")
        if not self.auth_manager._users:
            print("No users found.")
            return

        users_table = []
        for email, user in self.auth_manager._users.items():
            # Convert role number to role name
            role_name = UserRole.get_role_name(user.role) if isinstance(user.role, int) else user.role
            users_table.append([
                email,
                user.name,
                role_name  # Use the role name instead of the number
            ])
        print(tabulate(users_table, headers=["Email", "Name", "Role"], tablefmt="grid"))

    def change_user_role(self):
        email = input("\nEnter user email: ").strip()
        if email not in self.auth_manager._users:
            print("User not found.")
            return

        current_role_number = self.auth_manager._users[email].role
        current_role_name = UserRole.get_role_name(current_role_number)
        print(f"\nCurrent role: {current_role_name}")

        # Display roles with numbers and names
        UserRole.display_options()

        try:
            role_number = int(input("\nEnter role number: "))
            if role_number not in self.auth_manager._valid_roles:
                print("Invalid role number.")
                return

            new_role_name = UserRole.get_role_name(role_number)
            
            # Get existing user data
            old_user = self.auth_manager._users[email]
            
            # Create new UserCredentials with updated role
            self.auth_manager._users[email] = UserCredentials(
                email=email,
                password=old_user.password,
                role=role_number,
                name=old_user.name if hasattr(old_user, 'name') else email.split('@')[0]
            )
            
            # Save changes immediately
            self.auth_manager._save_users()
            print(f"\nRole updated successfully for {email}!")
            print(f"Previous role: {current_role_name}")
            print(f"New role: {new_role_name}")
            
        except ValueError:
            print("Please enter a valid number.")
        except Exception as e:
            print(f"Error updating role: {str(e)}")
            print("Please try again.")

    def reset_user_password(self):
        email = input("\nEnter user email: ").strip()
        if email not in self.auth_manager._users:
            print("User not found.")
            return

        new_password = input("Enter new password: ").strip()
        if not new_password:
            print("Password cannot be empty.")
            return

        user = self.auth_manager._users[email]
        user.password = new_password
        self.auth_manager._save_users()
        print(f"Password reset successfully for {email}!")

    def update_user_details(self):
        email = input("\nEnter user email: ").strip()
        if email not in self.auth_manager._users:
            print("User not found.")
            return

        user = self.auth_manager._users[email]
        print("\nCurrent details:")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")

        print("\nEnter new details (press Enter to keep current value):")
        new_name = input("New name: ").strip()
        new_email = input("New email: ").strip()

        if new_name:
            user.name = new_name
        if new_email and new_email != email:
            if new_email in self.auth_manager._users:
                print("Email already exists.")
                return
            # Create new user credentials with updated email
            self.auth_manager._users[new_email] = user
            # Remove old email entry
            del self.auth_manager._users[email]

        self.auth_manager._save_users()
        print("User details updated successfully!")

    def delete_user(self):
        email = input("\nEnter user email: ").strip()
        if email not in self.auth_manager._users:
            print("User not found.")
            return

        confirm = input(f"Are you sure you want to delete user {email}? (y/n): ").strip().lower()
        if confirm == 'y':
            del self.auth_manager._users[email]
            self.auth_manager._save_users()
            print(f"User {email} deleted successfully!")
        else:
            print("Deletion cancelled.")
            
    def run(self):
        while True:
            print("\n=== Admin System ===")
            main_menu_options = [
                ["1", "Create Admin Account"],
                ["2", "Login"],
                ["3", "Admin Menu"],
                ["4", "Exit"]
            ]
            print(tabulate(main_menu_options, headers=["Option", "Description"], tablefmt="grid"))

            choice = input("Enter your choice (1-4): ").strip()

            if choice == "1":
                self.create_admin_account()
            elif choice == "2":
                self.login()
            elif choice == "3":
                if self.current_user:
                    self.admin_menu()
                else:
                    print("Please login first.")
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    auth_manager = AuthenticationManager()
    admin_cli = AdminCLI(auth_manager)
    admin_cli.run()
