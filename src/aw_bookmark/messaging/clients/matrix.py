import httpx
from typing import Optional, Dict, Any
from ..base import MessagingClient


class MatrixClient(MessagingClient):
    """
    Matrix messaging client using httpx.

    Configuration required:
        - homeserver: Matrix homeserver URL
        - access_token: Matrix access token
        - rooms: Dict mapping category names to room IDs
    """

    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate Matrix configuration."""
        required = ['homeserver', 'access_token', 'rooms']
        for field in required:
            if field not in self.config:
                return False, f"Matrix config missing required field: {field}"

        if not isinstance(self.config['rooms'], dict):
            return False, "Matrix 'rooms' must be a dictionary"

        return True, None

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

            # Prepare Matrix API request
            homeserver = self.config['homeserver'].rstrip('/')
            endpoint = f"{homeserver}/_matrix/client/r0/rooms/{room_id}/send/m.room.message"

            headers = {
                'Authorization': f"Bearer {self.config['access_token']}",
                'Content-Type': 'application/json'
            }

            body = {
                'msgtype': 'm.text',
                'body': message,
                'format': 'org.matrix.custom.html',
                'formatted_body': self._format_html(title, url)
            }

            # Send with timeout
            timeout = self.config.get('timeout', 5.0)

            with httpx.Client(timeout=timeout) as client:
                response = client.post(endpoint, json=body, headers=headers)
                response.raise_for_status()

            self.logger.info(f"Matrix message sent to {room_id}")
            return True

        except httpx.HTTPStatusError as e:
            self.logger.error(f"Matrix HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.TimeoutException:
            self.logger.error(f"Matrix timeout after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"Matrix send failed: {e}", exc_info=True)
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
