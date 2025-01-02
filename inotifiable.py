from abc import ABC, abstractmethod

class INotifiable(ABC):
    @abstractmethod
    def send_notification(self, message):
        """Send a notification with the given message."""
        pass

    @abstractmethod
    def get_notification_preferences(self):
        """Get the notification preferences for the user."""
        pass

    @abstractmethod
    def update_notification_preferences(self, preferences):
        """Update the notification preferences."""
        pass
