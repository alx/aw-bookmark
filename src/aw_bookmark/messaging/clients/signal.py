import httpx
from typing import Optional, List
from ..base import MessagingClient


class SignalClient(MessagingClient):
    """
    Signal messaging client using signal-cli-rest-api.

    Configuration required:
        - api_url: Base URL for signal-cli-rest-api
        - sender: Sender's phone number in international format
        - recipients: Dict mapping category names to recipient configs
            Each config contains:
                - individuals: List of phone numbers
                - groups: List of group IDs
    """

    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate Signal configuration."""
        required = ['api_url', 'sender', 'recipients']
        for field in required:
            if field not in self.config:
                return False, f"Signal config missing required field: {field}"

        sender = self.config['sender']
        if not self._is_valid_phone_number(sender):
            return False, f"Signal sender must be valid phone number starting with +: {sender}"

        recipients = self.config['recipients']
        if not isinstance(recipients, dict):
            return False, "Signal 'recipients' must be a dictionary"

        for category, recipient_config in recipients.items():
            if not isinstance(recipient_config, dict):
                return False, f"Signal recipients['{category}'] must be a dictionary"

            if 'individuals' in recipient_config:
                individuals = recipient_config['individuals']
                if not isinstance(individuals, list):
                    return False, f"Signal recipients['{category}']['individuals'] must be a list"

                for phone in individuals:
                    if not self._is_valid_phone_number(phone):
                        return False, f"Invalid phone number in '{category}': {phone}"

            if 'groups' in recipient_config:
                groups = recipient_config['groups']
                if not isinstance(groups, list):
                    return False, f"Signal recipients['{category}']['groups'] must be a list"

                for group_id in groups:
                    if not self._is_valid_group_id(group_id):
                        return False, f"Invalid group ID in '{category}': {group_id}"

            if 'individuals' not in recipient_config and 'groups' not in recipient_config:
                return False, f"Signal recipients['{category}'] must have 'individuals' or 'groups'"

        return True, None

    def send_message(self, url: str, title: str, category: Optional[str] = None) -> bool:
        """Send message to Signal recipients."""
        if not self.is_enabled():
            self.logger.debug("Signal client disabled, skipping send")
            return False

        try:
            recipient_list = self._get_recipients_for_category(category)
            if not recipient_list:
                self.logger.warning(f"No Signal recipients configured for category: {category}")
                return False

            message = self.format_message(url, title)

            api_url = self.config['api_url'].rstrip('/')
            endpoint = f"{api_url}/v2/send"

            headers = {
                'Content-Type': 'application/json'
            }

            body = {
                'message': message,
                'number': self.config['sender'],
                'recipients': recipient_list
            }

            timeout = self.config.get('timeout', 10.0)

            with httpx.Client(timeout=timeout) as client:
                response = client.post(endpoint, json=body, headers=headers)
                response.raise_for_status()

            self.logger.info(f"Signal message sent to {len(recipient_list)} recipient(s) for category '{category}'")
            return True

        except httpx.HTTPStatusError as e:
            self.logger.error(f"Signal HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.TimeoutException:
            self.logger.error(f"Signal timeout after {timeout}s")
            return False
        except httpx.RequestError as e:
            self.logger.error(f"Signal request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Signal send failed: {e}", exc_info=True)
            return False

    def _get_recipients_for_category(self, category: Optional[str]) -> List[str]:
        """Get combined list of recipients for category."""
        recipients = self.config['recipients']

        if category and category in recipients:
            recipient_config = recipients[category]
            result = []

            if 'individuals' in recipient_config:
                result.extend(recipient_config['individuals'])

            if 'groups' in recipient_config:
                result.extend(recipient_config['groups'])

            return result

        return []

    def _is_valid_phone_number(self, phone: str) -> bool:
        """Validate phone number format."""
        if not phone.startswith('+'):
            return False

        digits = phone[1:]
        return digits.isdigit() and len(digits) >= 7

    def _is_valid_group_id(self, group_id: str) -> bool:
        """Validate Signal group ID format."""
        return group_id.startswith('group.') and len(group_id) > 6
