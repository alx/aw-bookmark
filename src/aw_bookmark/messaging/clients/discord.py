import httpx
from typing import Optional
from ..base import MessagingClient


class DiscordClient(MessagingClient):
    """
    Discord bot messaging client using Discord REST API.

    Configuration required:
        - bot_token: Discord bot token
        - channel_ids: Dict mapping category names to Discord channel IDs
        - message_template: Optional message format string (default: '🔖 {title}\n{url}')
        - timeout: Optional request timeout in seconds (default: 5.0)

    Example configuration:
        {
            'enabled': True,
            'bot_token': 'YOUR_BOT_TOKEN_HERE',
            'channel_ids': {
                'work': '123456789012345678',
                'personal': '987654321098765432',
                'default': '111111111111111111'
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
        if 'bot_token' not in self.config:
            return False, "Discord config missing required field: bot_token"

        if 'channel_ids' not in self.config:
            return False, "Discord config missing required field: channel_ids"

        # Validate bot_token is a string
        bot_token = self.config['bot_token']
        if not isinstance(bot_token, str):
            return False, "Discord 'bot_token' must be a string"

        # Validate bot_token format
        if not self._is_valid_bot_token(bot_token):
            return False, "Invalid Discord bot token format"

        # Validate channel_ids is a dict
        channel_ids = self.config['channel_ids']
        if not isinstance(channel_ids, dict):
            return False, "Discord 'channel_ids' must be a dictionary"

        # Validate each channel ID
        for category, channel_id in channel_ids.items():
            if not isinstance(channel_id, str):
                return False, f"Discord channel_ids['{category}'] must be a string"

            # Validate channel ID format (Discord snowflake)
            if not self._is_valid_channel_id(channel_id):
                return False, f"Invalid Discord channel ID for category '{category}': {channel_id}"

        return True, None

    def send_message(self, url: str, title: str, category: Optional[str] = None) -> bool:
        """
        Send message to Discord channel using bot API.

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
            # Get channel ID for category
            channel_id = self._get_channel_for_category(category)
            if not channel_id:
                self.logger.warning(f"No Discord channel configured for category: {category}")
                return False

            # Format message
            message = self.format_message(url, title)

            # Prepare Discord API request
            # Discord REST API endpoint for sending messages
            endpoint = f"https://discord.com/api/v10/channels/{channel_id}/messages"

            # Prepare authentication header
            bot_token = self.config['bot_token']
            if not bot_token.startswith('Bot '):
                bot_token = f'Bot {bot_token}'

            headers = {
                'Authorization': bot_token,
                'Content-Type': 'application/json'
            }

            body = {
                'content': message
            }

            # Send with timeout
            timeout = self.config.get('timeout', 5.0)

            with httpx.Client(timeout=timeout) as client:
                response = client.post(endpoint, json=body, headers=headers)
                response.raise_for_status()

            self.logger.info(f"Discord message sent to channel {channel_id} for category '{category}'")
            return True

        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors from Discord API
            status = e.response.status_code
            if status == 401:
                self.logger.error("Discord authentication failed. Check bot_token.")
            elif status == 403:
                self.logger.error(f"Discord bot lacks permission to send messages in channel {channel_id}")
            elif status == 404:
                self.logger.error(f"Discord channel {channel_id} not found. Bot may lack access.")
            else:
                self.logger.error(f"Discord HTTP error: {status} - {e.response.text}")
            return False
        except httpx.TimeoutException:
            timeout = self.config.get('timeout', 5.0)
            self.logger.error(f"Discord timeout after {timeout}s")
            return False
        except httpx.RequestError as e:
            self.logger.error(f"Discord request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Discord send failed: {e}", exc_info=True)
            return False

    def _get_channel_for_category(self, category: Optional[str]) -> Optional[str]:
        """
        Get channel ID for category.

        Args:
            category: Category name or None

        Returns:
            Channel ID as string if found, None otherwise
        """
        channel_ids = self.config['channel_ids']

        # Check if category exists in channel_ids
        if category and category in channel_ids:
            return channel_ids[category]

        # Fall back to default
        if 'default' in channel_ids:
            return channel_ids['default']

        return None

    def _is_valid_bot_token(self, token: str) -> bool:
        """
        Validate Discord bot token format.

        Discord bot tokens are base64-encoded and follow the format:
        {user_id}.{timestamp}.{hmac}

        Args:
            token: Bot token to validate

        Returns:
            True if valid format, False otherwise
        """
        # Remove 'Bot ' prefix if present
        if token.startswith('Bot '):
            token = token[4:]

        # Discord bot tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return False

        # Check length and charset (alphanumeric plus ._-)
        return len(token) >= 50 and all(c.isalnum() or c in '._-' for c in token)

    def _is_valid_channel_id(self, channel_id: str) -> bool:
        """
        Validate Discord channel ID (snowflake).

        Discord snowflakes are 17-20 digit integers.

        Args:
            channel_id: Channel ID to validate

        Returns:
            True if valid snowflake format, False otherwise
        """
        # Discord snowflakes are 17-20 digit integers
        return channel_id.isdigit() and 17 <= len(channel_id) <= 20
