import httpx
from typing import Optional, List
from ..base import MessagingClient


class WhatsAppClient(MessagingClient):
    """
    WhatsApp messaging client using whatsapp-web.js REST API.

    Configuration required:
        - api_url: Base URL for whatsapp-web.js REST API
        - session: Session name for multi-device support (optional, defaults to 'default')
        - recipients: Dict mapping category names to recipient configs
            Each config contains:
                - individuals: List of phone numbers
                - groups: List of WhatsApp group IDs
    """

    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate WhatsApp configuration."""
        required = ['api_url', 'recipients']
        for field in required:
            if field not in self.config:
                return False, f"WhatsApp config missing required field: {field}"

        recipients = self.config['recipients']
        if not isinstance(recipients, dict):
            return False, "WhatsApp 'recipients' must be a dictionary"

        for category, recipient_config in recipients.items():
            if not isinstance(recipient_config, dict):
                return False, f"WhatsApp recipients['{category}'] must be a dictionary"

            if 'individuals' in recipient_config:
                individuals = recipient_config['individuals']
                if not isinstance(individuals, list):
                    return False, f"WhatsApp recipients['{category}']['individuals'] must be a list"

                for phone in individuals:
                    if not self._is_valid_phone_number(phone):
                        return False, f"Invalid phone number in '{category}': {phone}"

            if 'groups' in recipient_config:
                groups = recipient_config['groups']
                if not isinstance(groups, list):
                    return False, f"WhatsApp recipients['{category}']['groups'] must be a list"

                for group_id in groups:
                    if not self._is_valid_group_id(group_id):
                        return False, f"Invalid group ID in '{category}': {group_id}"

            if 'individuals' not in recipient_config and 'groups' not in recipient_config:
                return False, f"WhatsApp recipients['{category}'] must have 'individuals' or 'groups'"

        return True, None

    def send_message(self, url: str, title: str, category: Optional[str] = None) -> bool:
        """Send message to WhatsApp recipients."""
        if not self.is_enabled():
            self.logger.debug("WhatsApp client disabled, skipping send")
            return False

        try:
            recipient_list = self._get_recipients_for_category(category)
            if not recipient_list:
                self.logger.warning(f"No WhatsApp recipients configured for category: {category}")
                return False

            message = self.format_message(url, title)

            api_url = self.config['api_url'].rstrip('/')
            endpoint = f"{api_url}/v1/messages"

            session = self.config.get('session', 'default')

            headers = {
                'Content-Type': 'application/json'
            }

            body = {
                'session': session,
                'recipients': recipient_list,
                'message': message
            }

            timeout = self.config.get('timeout', 10.0)

            with httpx.Client(timeout=timeout) as client:
                response = client.post(endpoint, json=body, headers=headers)
                response.raise_for_status()

            self.logger.info(f"WhatsApp message sent to {len(recipient_list)} recipient(s) for category '{category}'")
            return True

        except httpx.HTTPStatusError as e:
            self.logger.error(f"WhatsApp HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.TimeoutException:
            self.logger.error(f"WhatsApp timeout after {timeout}s")
            return False
        except httpx.RequestError as e:
            self.logger.error(f"WhatsApp request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"WhatsApp send failed: {e}", exc_info=True)
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
        """Validate WhatsApp group ID format."""
        return group_id.endswith('@g.us') and len(group_id) > 8
