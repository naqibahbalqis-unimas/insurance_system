from enum import Enum

class PolicyType(Enum):
    LIFE = 1
    CAR = 2
    HEALTH = 3
    PROPERTY = 4
    
    @classmethod
    def get_type_name(cls, number: int) -> str:
        """Get policy type name from number"""
        for policy_type in cls:
            if policy_type.value == number:
                return policy_type.name
        raise ValueError(f"No policy type with number {number}")
    
    @classmethod
    def display_options(cls) -> None:
        """Display all policy type options"""
        print("\nAvailable Policy Types:")
        for policy_type in cls:
            print(f"{policy_type.value}. {policy_type.name}")


class PolicyStatus(Enum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    ACTIVE = 4
    INACTIVE = 5
    EXPIRED = 6
    CANCELLED = 7

    @classmethod
    def get_status_name(cls, value: int) -> str:
        """Get status name from value"""
        for status in cls:
            if status.value == value:
                return status.name
        raise ValueError(f"No status with value {value}")

    @classmethod
    def display_options(cls) -> None:
        """Display all status options with numbers"""
        print("\nAvailable Statuses:")
        for status in cls:
            print(f"{status.value}. {status.name}")
