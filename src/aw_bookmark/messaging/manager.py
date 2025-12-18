import logging
import threading
from typing import Dict, List, Optional, Any
from .base import MessagingClient


class MessagingManager:
    """
    Coordinates message sending across multiple clients.

    Handles:
    - Client initialization and validation
    - Category-based routing
    - Asynchronous/threaded message dispatch
    - Error aggregation and logging
    """

    def __init__(self, clients: Dict[str, MessagingClient], routing: Dict[str, List[str]]):
        """
        Initialize manager with clients and routing config.

        Args:
            clients: Dict mapping client name to MessagingClient instance
            routing: Dict mapping category to list of client names
        """
        self.clients = clients
        self.routing = routing
        self.logger = logging.getLogger('MessagingManager')

    def send_async(self, url: str, title: str, category: Optional[str] = None):
        """
        Send message asynchronously to all configured clients for category.

        Args:
            url: Bookmark URL
            title: Bookmark title
            category: Optional category for routing
        """
        # Determine which clients to notify
        client_names = self._get_clients_for_category(category)

        self.logger.info(f"[ROUTING] Initiating for category='{category}', url={url[:60]}{'...' if len(url) > 60 else ''}, targets={len(client_names)} clients{f': {client_names}' if client_names else ''}")

        if not client_names:
            self.logger.info(f"[ROUTING] No clients configured for category: {category}")
            return

        # Send in background thread to avoid blocking request
        thread = threading.Thread(
            target=self._send_to_clients,
            args=(client_names, url, title, category),
            daemon=True  # Don't prevent shutdown
        )
        thread.start()
        self.logger.debug(f"[THREAD] Started async dispatch for category='{category}', thread={thread.name}")

    def _send_to_clients(self, client_names: List[str], url: str, title: str, category: Optional[str]):
        """Internal method to send to multiple clients (runs in thread)."""
        self.logger.debug(f"[THREAD] Worker started for category='{category}', processing {len(client_names)} clients")

        success_count = 0
        failure_count = 0
        skipped_count = 0

        for client_name in client_names:
            client = self.clients.get(client_name)

            if not client:
                self.logger.warning(f"[DISPATCH] Client '{client_name}' not found in registry")
                skipped_count += 1
                continue

            if not client.is_enabled():
                self.logger.info(f"[DISPATCH] Client '{client_name}' disabled, skipping")
                skipped_count += 1
                continue

            self.logger.debug(f"[DISPATCH] Sending to {client_name}: url={url[:60]}{'...' if len(url) > 60 else ''}, title={title[:40]}{'...' if len(title) > 40 else ''}")

            try:
                success = client.send_message(url, title, category)
                if success:
                    self.logger.info(f"[DISPATCH] ✓ Sent to {client_name}")
                    success_count += 1
                else:
                    self.logger.warning(f"[DISPATCH] ✗ Failed to send to {client_name}")
                    failure_count += 1
            except Exception as e:
                # Safety net - client implementations should not raise
                self.logger.error(f"[DISPATCH] Unexpected error from {client_name}: {e}", exc_info=True)
                failure_count += 1

        self.logger.info(f"[SUMMARY] category='{category}', clients_targeted={len(client_names)}, sent={success_count}, failed={failure_count}, skipped={skipped_count}")
        self.logger.debug(f"[THREAD] Worker completed for category='{category}'")

    def _get_clients_for_category(self, category: Optional[str]) -> List[str]:
        """Get list of client names for category."""
        if category and category in self.routing:
            clients = self.routing[category]
            self.logger.info(f"[CATEGORY] '{category}' matched routing rule → {clients}")
            return clients

        self.logger.info(f"[CATEGORY] No routing rule for '{category}' → no clients selected")
        return []

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> Optional['MessagingManager']:
        """
        Factory method to create MessagingManager from config dict.

        Args:
            config: Messaging configuration dictionary

        Returns:
            MessagingManager instance or None if messaging disabled
        """
        if not config.get('enabled', False):
            return None

        # Import client classes
        from .clients.matrix import MatrixClient
        from .clients.signal import SignalClient
        from .clients.discord import DiscordClient
        from .clients.whatsapp import WhatsAppClient

        client_classes = {
            'matrix': MatrixClient,
            'signal': SignalClient,
            'discord': DiscordClient,
            'whatsapp': WhatsAppClient,
        }

        # Initialize enabled clients
        clients = {}
        client_configs = config.get('clients', {})

        logger = logging.getLogger('MessagingManager')

        for client_name, client_class in client_classes.items():
            client_config = client_configs.get(client_name, {})

            if not client_config.get('enabled', False):
                continue

            try:
                client = client_class(client_config)
                is_valid, error_msg = client.validate_config()

                if not is_valid:
                    logger.error(f"Invalid {client_name} config: {error_msg}")
                    continue

                clients[client_name] = client
                logger.info(f"Initialized {client_name} client")

            except Exception as e:
                logger.error(f"Failed to initialize {client_name}: {e}", exc_info=True)

        if not clients:
            logger.warning("No messaging clients configured")
            return None

        routing = config.get('category_routing', {'_default': []})

        return cls(clients, routing)
