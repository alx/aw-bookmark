import httpx
from typing import Optional
from ..base import MessagingClient


class DiscordClient(MessagingClient):
    """
    Discord webhook messaging client.

    Configuration required:
        - webhook_urls: Dict mapping category names to webhook URLs
        - message_template: Optional message format string (default: '🔖 {title}\n{url}')
        - timeout: Optional request timeout in seconds (default: 5.0)

    Example configuration:
        {
            'enabled': True,
            'webhook_urls': {
                'work': 'https://discord.com/api/webhooks/123456789/token',
                'personal': 'https://discord.com/api/webhooks/987654321/token'
            },
            'message_template': '🔖 **{title}**\n{url}',
            'timeout': 5.0
        }
    """

    def validate_config(self) -> tuple[bool, Optional[str]]:
        """
        Validate Discord configuration.

        Returns:
            (is_valid, error_message) tuple
        """
        # Check required fields
        required = ['webhook_urls']
        for field in required:
            if field not in self.config:
                return False, f"Discord config missing required field: {field}"

        # Validate webhook_urls is a dict
        webhook_urls = self.config['webhook_urls']
        if not isinstance(webhook_urls, dict):
            return False, "Discord 'webhook_urls' must be a dictionary"

        # Validate each webhook URL format
        for category, url in webhook_urls.items():
            if not isinstance(url, str):
                return False, f"Discord webhook_urls['{category}'] must be a string"

            # Validate URL format
            if not self._is_valid_webhook_url(url):
                return False, f"Invalid webhook URL for category '{category}': {url}"

        return True, None

    def send_message(self, url: str, title: str, category: Optional[str] = None) -> bool:
        """
        Send message to Discord webhook.

        Args:
            url: Bookmark URL
            title: Bookmark title
            category: Optional category for routing

        Returns:
            True if message sent successfully, False otherwise
        """
        # Check if enabled
        if not self.is_enabled():
            self.logger.debug("Discord client disabled, skipping send")
            return False

        try:
            # Determine target webhook
            webhook_url = self._get_webhook_for_category(category)
            if not webhook_url:
                self.logger.warning(f"No Discord webhook configured for category: {category}")
                return False

            # Format message
            message = self.format_message(url, title)

            # Prepare Discord webhook request
            # Discord webhook expects JSON with "content" field
            body = {
                'content': message
            }

            headers = {
                'Content-Type': 'application/json'
            }

            # Send with timeout
            timeout = self.config.get('timeout', 5.0)

            with httpx.Client(timeout=timeout) as client:
                response = client.post(webhook_url, json=body, headers=headers)
                response.raise_for_status()

            self.logger.info(f"Discord message sent for category '{category}'")
            return True

        except httpx.HTTPStatusError as e:
            self.logger.error(f"Discord HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.TimeoutException:
            self.logger.error(f"Discord timeout after {timeout}s")
            return False
        except httpx.RequestError as e:
            self.logger.error(f"Discord request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Discord send failed: {e}", exc_info=True)
            return False

    def _get_webhook_for_category(self, category: Optional[str]) -> Optional[str]:
        """
        Get webhook URL for category.

        Args:
            category: Category name or None

        Returns:
            Webhook URL if found, None otherwise
        """
        webhook_urls = self.config['webhook_urls']

        # Check if category exists in webhook_urls
        if category and category in webhook_urls:
            return webhook_urls[category]

        return None

    def _is_valid_webhook_url(self, url: str) -> bool:
        """
        Validate Discord webhook URL format.

        Valid format: https://discord.com/api/webhooks/{webhook_id}/{webhook_token}
        - Must start with https://discord.com/api/webhooks/ or https://discordapp.com/api/webhooks/
        - Must have webhook ID (numeric, at least 17 chars - Discord snowflake)
        - Must have webhook token (at least 10 chars)

        Args:
            url: Webhook URL to validate

        Returns:
            True if valid, False otherwise
        """
        if not url.startswith(('https://discord.com/api/webhooks/',
                              'https://discordapp.com/api/webhooks/')):
            return False

        # Extract path after /webhooks/
        parts = url.split('/webhooks/')
        if len(parts) != 2:
            return False

        webhook_path = parts[1]
        path_parts = webhook_path.split('/')

        # Must have at least webhook_id/token
        if len(path_parts) < 2:
            return False

        webhook_id, webhook_token = path_parts[0], path_parts[1]

        # Webhook ID should be numeric (Discord snowflake)
        if not webhook_id.isdigit() or len(webhook_id) < 17:
            return False

        # Webhook token should exist and be reasonable length
        if not webhook_token or len(webhook_token) < 10:
            return False

        return True
