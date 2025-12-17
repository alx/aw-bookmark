from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging


class MessagingClient(ABC):
    """
    Abstract base class for all messaging integrations.

    Subclasses must implement send_message() to handle actual API calls.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize messaging client with configuration.

        Args:
            config: Client-specific configuration dictionary
            logger: Optional logger instance (creates one if not provided)
        """
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.enabled = config.get('enabled', True)

    @abstractmethod
    def send_message(self, url: str, title: str, category: Optional[str] = None) -> bool:
        """
        Send a bookmark notification message.

        Args:
            url: Bookmark URL
            title: Bookmark title
            category: Optional category for routing

        Returns:
            True if message sent successfully, False otherwise

        Note:
            Implementations should catch all exceptions and return False on error.
            Should log errors but never raise exceptions.
        """
        pass

    def format_message(self, url: str, title: str) -> str:
        """
        Format the message using configured template.

        Args:
            url: Bookmark URL
            title: Bookmark title

        Returns:
            Formatted message string
        """
        template = self.config.get('message_template', '🔖 {title}\n{url}')
        return template.format(title=title, url=url)

    def is_enabled(self) -> bool:
        """Check if this client is enabled."""
        return self.enabled

    @abstractmethod
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """
        Validate client configuration.

        Returns:
            (is_valid, error_message) tuple
        """
        pass
