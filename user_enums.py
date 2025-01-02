from enum import Enum

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