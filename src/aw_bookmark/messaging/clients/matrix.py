import httpx
import logging
from typing import Optional, Dict, Any
from ..base import MessagingClient


class MatrixClient(MessagingClient):
    """
    Matrix messaging client using httpx.

    Configuration required:
        - homeserver: Matrix homeserver URL
        - rooms: Dict mapping category names to room IDs

    Authentication (one of the following):
        - user_id + password: Recommended. Client will login and manage tokens automatically.
        - access_token: Static token (may expire if refresh tokens are enabled on homeserver)
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        super().__init__(config, logger)
        self._cached_access_token: Optional[str] = None

    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate Matrix configuration."""
        required = ['homeserver', 'rooms']
        for field in required:
            if field not in self.config:
                return False, f"Matrix config missing required field: {field}"

        if not isinstance(self.config['rooms'], dict):
            return False, "Matrix 'rooms' must be a dictionary"

        # Check for authentication method
        has_password_auth = 'user_id' in self.config and 'password' in self.config
        has_token_auth = 'access_token' in self.config

        if not has_password_auth and not has_token_auth:
            return False, "Matrix config requires either (user_id + password) or access_token"

        return True, None

    def _login(self) -> Optional[str]:
        """
        Login to Matrix homeserver and obtain access token.
        Returns the access token or None on failure.
        """
        homeserver = self.config['homeserver'].rstrip('/')
        login_url = f"{homeserver}/_matrix/client/v3/login"

        payload = {
            "type": "m.login.password",
            "identifier": {
                "type": "m.id.user",
                "user": self.config['user_id']
            },
            "password": self.config['password'],
            "initial_device_display_name": "aw-bookmark"
        }

        timeout = self.config.get('timeout', 5.0)

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(login_url, json=payload)
                response.raise_for_status()
                data = response.json()
                access_token = data.get('access_token')
                if access_token:
                    self.logger.info(f"Matrix login successful for {self.config['user_id']}")
                    return access_token
                else:
                    self.logger.error("Matrix login response missing access_token")
                    return None
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Matrix login failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            self.logger.error(f"Matrix login error: {e}", exc_info=True)
            return None

    def _get_access_token(self) -> Optional[str]:
        """
        Get a valid access token, either from cache, config, or by logging in.
        """
        # If using password auth, login and cache the token
        if 'user_id' in self.config and 'password' in self.config:
            if self._cached_access_token is None:
                self._cached_access_token = self._login()
            return self._cached_access_token

        # Fall back to static access_token from config
        return self.config.get('access_token')

    def send_message(self, url: str, title: str, category: Optional[str] = None) -> bool:
        """Send message to Matrix room."""
        if not self.is_enabled():
            self.logger.debug("Matrix client disabled, skipping send")
            return False

        try:
            # Determine target room
            room_id = self._get_room_for_category(category)
            if not room_id:
                self.logger.warning(f"No Matrix room configured for category: {category}")
                return False

            # Format message
            message = self.format_message(url, title)

            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                self.logger.error("Matrix: No access token available")
                return False

            # Try to send, retry once with fresh login if token expired
            result = self._send_to_room(room_id, message, title, url, access_token)

            # If failed with 401 and using password auth, try to re-login
            if result == 401 and 'user_id' in self.config and 'password' in self.config:
                self.logger.info("Matrix token expired, re-authenticating...")
                self._cached_access_token = None  # Clear cached token
                access_token = self._get_access_token()
                if access_token:
                    result = self._send_to_room(room_id, message, title, url, access_token)

            return result is True

        except Exception as e:
            self.logger.error(f"Matrix send failed: {e}", exc_info=True)
            return False

    def _send_to_room(self, room_id: str, message: str, title: str, url: str, access_token: str) -> bool | int:
        """
        Send message to a specific room.
        Returns True on success, HTTP status code on HTTP error, False on other errors.
        """
        timeout = self.config.get('timeout', 5.0)
        try:
            homeserver = self.config['homeserver'].rstrip('/')
            endpoint = f"{homeserver}/_matrix/client/v3/rooms/{room_id}/send/m.room.message"

            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }

            body = {
                'msgtype': 'm.text',
                'body': message,
                'format': 'org.matrix.custom.html',
                'formatted_body': self._format_html(title, url)
            }

            with httpx.Client(timeout=timeout) as client:
                response = client.post(endpoint, json=body, headers=headers)
                response.raise_for_status()

            self.logger.info(f"Matrix message sent to {room_id}")
            return True

        except httpx.HTTPStatusError as e:
            self.logger.error(f"Matrix HTTP error: {e.response.status_code} - {e.response.text}")
            return e.response.status_code
        except httpx.TimeoutException:
            self.logger.error(f"Matrix timeout after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"Matrix send error: {e}", exc_info=True)
            return False

    def _get_room_for_category(self, category: Optional[str]) -> Optional[str]:
        """Get room ID for category."""
        rooms = self.config['rooms']

        if category and category in rooms:
            return rooms[category]

        return None

    def _format_html(self, title: str, url: str) -> str:
        """Format message as HTML for Matrix rich text."""
        return f'🔖 <strong>{title}</strong><br/><a href="{url}">{url}</a>'
