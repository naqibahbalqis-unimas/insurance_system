##auth.py
from datetime import date, datetime
from typing import Dict, Optional, Tuple
import hashlib
import re
import jwt
import os
import time
from dataclasses import dataclass, asdict
from data_storage import DataStorage  # Add this imports
from user_enums import UserRole  # Add this import
from enum import Enum


@dataclass
class UserCredentials:
    email: str
    password: str
    role: str
    name: str = ""  # Add name field with default empty string
    


class UserRole(Enum):
    CUSTOMER = 1
    ADMIN = 2
    CLAIM_ADJUSTER = 3
    AGENT = 4
    UNDERWRITER = 5

    @classmethod
    def get_role_name(cls, number: int) -> str:
        """Get role name from number"""
        try:
            return cls(number).name.lower().replace('_', ' ')
        except ValueError:
            return 'customer'  # Default role

    @classmethod
    def display_options(cls):
        """Display all role options with numbers"""
        print("\nAvailable roles:")
        for role in cls:
            print(f"{role.value}. {role.name.lower().replace('_', ' ')}")

    @classmethod
    def get_role(cls, number: int) -> 'UserRole':
        """Get role enum from number"""
        try:
            return cls(number)
        except ValueError:
            return cls.CUSTOMER

class AuthenticationManager:
    def __init__(self):
        self._users: Dict[str, UserCredentials] = {}
        self._secret_key = "your-secret-key"
        self._token_expiry = 24 * 60 * 60  # 24 hours
        self._storage = DataStorage()
        self._valid_roles = [role.value for role in UserRole]  # Store role numbers
        self._load_users()
        
    
    def get_user_role_display(self, email: str) -> str:
        """Get user role display name"""
        if email in self._users:
            role_number = self._users[email].role
            return UserRole.get_role_name(role_number)
        return "customer"

    def register(self, email: str, password: str, role: UserRole) -> Tuple[bool, str]:
        try:
            if not self._validate_email(email):
                return False, "Invalid email format"

            if email in self._users:
                return False, "Email already registered"

            name = email.split('@')[0]
            self._users[email] = UserCredentials(
                email=email,
                password=password,
                role=role.value,  # Store the role value instead of enum
                name=name
            )

            self._save_users()
            return True, "Registration successful"
        except Exception as e:
            return False, f"Registration error: {str(e)}"
   
    def _load_users(self):
        """Load users from storage"""
        try:
            users_data = self._storage.load_data("users")
            for email, user_data in users_data.items():
                self._users[email] = UserCredentials(
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    name=user_data.get('name', "")  # Load name if available
                )
        except Exception as e:
            print(f"Error loading users: {str(e)}")


    def _save_users(self):
        try:
            users_data = {}
            for email, user_creds in self._users.items():
                users_data[email] = {
                    'email': user_creds.email,
                    'password': user_creds.password,
                    'role': user_creds.role,  # This will now be the integer value
                    'name': user_creds.name
                }

            saved = self._storage.save_data("users", users_data)
            if not saved:
                raise ValueError("Failed to save data to storage")
        except Exception as e:
            print(f"Error in _save_users: {str(e)}")
                
            
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        return '@' in email and '.' in email.split('@')[1]

    def _generate_token(self, email: str, role: str) -> str:
        """Generate JWT token"""
        try:
            payload = {
                'email': email,
                'role': role,
                'exp': datetime.utcnow().timestamp() + self._token_expiry
            }
            token = jwt.encode(
                payload,
                self._secret_key,
                algorithm='HS256'
            )
            # PyJWT >= 2.0.0 returns string directly
            if isinstance(token, bytes):
                return token.decode('utf-8')
            return token
        except Exception as e:
            print(f"Token generation error: {str(e)}")
            return ""

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Login user
        Returns: (success: bool, token_or_message: str)
        """
        try:
            # Check if user exists
            if email not in self._users:
                return False, "Invalid email or password"

            # Verify password
            user = self._users[email]
            if password != user.password:
                return False, "Invalid email or password"

            # Generate token
            token = self._generate_token(email, user.role)
            if not token:
                return False, "Error generating token"

            return True, token
        except Exception as e:
            return False, f"Login error: {str(e)}"

    def verify_token(self, token: str) -> Tuple[bool, Dict]:
        """
        Verify JWT token
        Returns: (success: bool, payload: Dict)
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=['HS256'])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "Invalid token"}
        except Exception as e:
            return False, {"error": f"Verification error: {str(e)}"}

    def change_password(self, email: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        try:
            # Verify old password
            success, _ = self.login(email, old_password)
            if not success:
                return False, "Current password is incorrect"

            # Update password
            user = self._users[email]
            user.password = new_password
            return True, "Password changed successfully"
        except Exception as e:
            return False, f"Password change error: {str(e)}"

    def reset_password(self, email: str) -> Tuple[bool, str]:
        """
        Initiate password reset
        In production, this would send an email with reset link
        """
        try:
            if email not in self._users:
                return False, "Email not found"

            # Generate reset token
            reset_token = self._generate_token(email, 'reset')
            if not reset_token:
                return False, "Error generating reset token"

            print(f"Password reset token for {email}: {reset_token}")
            return True, "Password reset instructions sent to email"
        except Exception as e:
            return False, f"Password reset error: {str(e)}"

class AuthCLI:
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.current_user = None
        self.current_token = None
        self.user_manager = None  # Will be set by MainSystem

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self):
        """Display the main menu"""
        self.clear_screen()
        print("\n=== Authentication System ===")
        print("1. Register")
        print("2. Login")
        print("3. Reset Password")
        print("4. Exit")
        print("==========================")

    def display_logged_in_menu(self):
        """Display menu for logged-in users"""
        self.clear_screen()
        print(f"\n=== Welcome {self.current_user} ===")
        print("1. Change Password")
        print("2. View Profile")
        print("3. Logout")
        print("==========================")
        
    def register(self):
        print("\n=== User Registration ===")
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        
        print("\nSelect role:")
        UserRole.display_options()
        
        try:
            role_choice = int(input("Enter role number (1-5): ").strip())
            role = UserRole(role_choice)  # Convert directly to enum
            
            success, message = self.auth_manager.register(email, password, role)
            if success and self.user_manager:
                self.user_manager.create_user(email, password)
            print(f"\n{message}")
        except ValueError:
            print("Invalid role selection")
        
        input("\nPress Enter to continue...")
        
    def login(self):
        """Handle user login"""
        self.clear_screen()
        print("\n=== User Login ===")
        
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()

        success, token = self.auth_manager.login(email, password)
        
        if success:
            self.current_user = email
            self.current_token = token
            print("\nLogin successful!")
            time.sleep(1)
            return True
        else:
            print(f"\nLogin failed: {token}")
            input("\nPress Enter to continue...")
            return False

    def reset_password(self):
        """Handle password reset"""
        self.clear_screen()
        print("\n=== Password Reset ===")
        
        email = input("Enter email: ").strip()
        success, message = self.auth_manager.reset_password(email)
        print(f"\n{message}")
        input("\nPress Enter to continue...")

    def change_password(self):
        """Handle password change"""
        self.clear_screen()
        print("\n=== Change Password ===")
        
        old_password = input("Enter current password: ").strip()
        new_password = input("Enter new password: ").strip()
        
        success, message = self.auth_manager.change_password(
            self.current_user, old_password, new_password
        )
        print(f"\n{message}")
        input("\nPress Enter to continue...")

    def view_profile(self):
        """Display user profile"""
        self.clear_screen()
        print("\n=== User Profile ===")
        success, payload = self.auth_manager.verify_token(self.current_token)
        
        if success:
            print(f"Email: {payload['email']}")
            print(f"Role: {payload['role']}")
            print(f"Token expiry: {payload['exp']}")
        else:
            print("Error accessing profile")
        
        input("\nPress Enter to continue...")

    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.current_token = None
        print("\nLogged out successfully!")
        time.sleep(1)

    def run(self):
        """Main CLI loop"""
        while True:
            if self.current_user is None:
                self.display_menu()
                choice = input("\nEnter your choice (1-4): ").strip()

                if choice == '1':
                    self.register()
                elif choice == '2':
                    if self.login():
                        continue
                elif choice == '3':
                    self.reset_password()
                elif choice == '4':
                    print("\nGoodbye!")
                    break
                else:
                    print("\nInvalid choice. Please try again.")
                    time.sleep(1)
            else:
                self.display_logged_in_menu()
                choice = input("\nEnter your choice (1-3): ").strip()

                if choice == '1':
                    self.change_password()
                elif choice == '2':
                    self.view_profile()
                elif choice == '3':
                    self.logout()
                else:
                    print("\nInvalid choice. Please try again.")
                    time.sleep(1)

if __name__ == "__main__":
    try:
        import jwt
        print("PyJWT version:", jwt.__version__)
        cli = AuthCLI()
        cli.run()
    except ImportError:
        print("PyJWT is not installed. Please install it using:")
        print("pip install PyJWT")