#!/usr/bin/env python3
"""
Integration test for Discord messaging client.
Requires a valid Discord webhook URL.

To run:
1. Create a Discord webhook:
   - Open Discord server settings
   - Go to Integrations → Webhooks
   - Create New Webhook
   - Copy the webhook URL
2. Configure WEBHOOK_URL below
3. Run: uv run python test_discord.py
"""

import logging
from aw_bookmark.messaging.clients.discord import DiscordClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# CONFIGURE THIS VALUE BEFORE RUNNING
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

print("="*60)
print("Discord Client Integration Test")
print("="*60)
print("\nWARNING: This will send an actual Discord message!")
print(f"Webhook: {WEBHOOK_URL[:50]}...")
print("\nMake sure you have a valid Discord webhook URL configured.")
print("="*60)

# Test configuration
config = {
    'enabled': True,
    'webhook_urls': {
        'test': WEBHOOK_URL
    },
    'message_template': '🔖 **{title}**\n{url}',
    'timeout': 5.0
}

# Initialize client
print("\n[1/4] Initializing Discord client...")
client = DiscordClient(config)

# Validate config
print("[2/4] Validating configuration...")
is_valid, error = client.validate_config()
if not is_valid:
    print(f"✗ Config validation failed: {error}")
    exit(1)
print("✓ Config is valid")

# Test sending message
print("[3/4] Sending test message...")
success = client.send_message(
    url='https://example.com/test-bookmark',
    title='Test Bookmark from aw-bookmark Discord Client',
    category='test'
)

print("[4/4] Checking result...")
if success:
    print("✓ SUCCESS: Message sent successfully!")
    print("\nCheck your Discord channel!")
    print("You should see the test bookmark message.")
else:
    print("✗ FAILED: Message was not sent")
    print("\nTroubleshooting:")
    print("1. Is the webhook URL valid?")
    print("2. Has the webhook been deleted?")
    print("3. Is Discord reachable from your network?")
    print("4. Check the logs above for error details")

print("\n" + "="*60)
print("Test completed")
print("="*60)
