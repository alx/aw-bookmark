#!/usr/bin/env python3
"""
Integration test for WhatsApp messaging client.
Requires whatsapp-web.js REST API running on http://localhost:3000

To run:
1. Start whatsapp-web.js REST API service (custom Node.js server)
2. Authenticate with WhatsApp (QR code scan)
3. Configure your actual phone numbers and group IDs below
4. Run: uv run python test_whatsapp.py
"""

import logging
from aw_bookmark.messaging.clients.whatsapp import WhatsAppClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# CONFIGURE THESE VALUES BEFORE RUNNING
TEST_RECIPIENT = "+1234567890"  # A phone number that can receive test messages
# TEST_GROUP_ID = "123456789@g.us"  # Optional: WhatsApp group ID for testing

print("="*60)
print("WhatsApp Client Integration Test")
print("="*60)
print("\nWARNING: This will send an actual WhatsApp message!")
print(f"Recipient: {TEST_RECIPIENT}")
print("\nMake sure whatsapp-web.js REST API is running on http://localhost:3000")
print("and authenticated with WhatsApp")
print("="*60)

# Test configuration
config = {
    'enabled': True,
    'api_url': 'http://localhost:3000',
    'session': 'default',
    'recipients': {
        'test': {
            'individuals': [TEST_RECIPIENT],
            'groups': []
        }
    },
    'message_template': '🔖 {title}\n{url}',
    'timeout': 10.0
}

# Initialize client
print("\n[1/4] Initializing WhatsApp client...")
client = WhatsAppClient(config)

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
    title='Test Bookmark from aw-bookmark WhatsApp Client',
    category='test'
)

print("[4/4] Checking result...")
if success:
    print("✓ SUCCESS: Message sent successfully!")
    print(f"\nCheck your WhatsApp on {TEST_RECIPIENT}")
    print("You should see the test bookmark message.")
else:
    print("✗ FAILED: Message was not sent")
    print("\nTroubleshooting:")
    print("1. Is whatsapp-web.js REST API running? Check: curl http://localhost:3000/health")
    print("2. Is WhatsApp authenticated? Check the QR code scan status")
    print(f"3. Is {TEST_RECIPIENT} a valid WhatsApp number?")
    print("4. Check the logs above for error details")
    print("5. Verify the API endpoint structure matches your whatsapp-web.js wrapper")

print("\n" + "="*60)
print("Test completed")
print("="*60)
