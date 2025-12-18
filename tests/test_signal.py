#!/usr/bin/env python3
"""
Integration test for Signal messaging client.
Requires signal-cli-rest-api running on http://localhost:8080

To run:
1. Start signal-cli-rest-api:
   docker run -d --name signal-api -p 8080:8080 \
     -v ~/signal-cli-config:/home/.local/share/signal-cli \
     bbernhard/signal-cli-rest-api:latest

2. Configure your actual phone numbers below
3. Run: uv run python test_signal.py
"""

import logging
from aw_bookmark.messaging.clients.signal import SignalClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# CONFIGURE THESE VALUES BEFORE RUNNING
SENDER_PHONE = "+1234567890"  # Your registered Signal sender number
TEST_RECIPIENT = "+9999999999"  # A phone number that can receive test messages
# TEST_GROUP_ID = "group.YOUR_GROUP_ID"  # Optional: Signal group ID for testing

print("="*60)
print("Signal Client Integration Test")
print("="*60)
print("\nWARNING: This will send an actual Signal message!")
print(f"Sender: {SENDER_PHONE}")
print(f"Recipient: {TEST_RECIPIENT}")
print("\nMake sure signal-cli-rest-api is running on http://localhost:8080")
print("="*60)

# Test configuration
config = {
    'enabled': True,
    'api_url': 'http://localhost:8080',
    'sender': SENDER_PHONE,
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
print("\n[1/4] Initializing Signal client...")
client = SignalClient(config)

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
    title='Test Bookmark from aw-bookmark Signal Client',
    category='test'
)

print("[4/4] Checking result...")
if success:
    print("✓ SUCCESS: Message sent successfully!")
    print(f"\nCheck your Signal app on {TEST_RECIPIENT}")
    print("You should see the test bookmark message.")
else:
    print("✗ FAILED: Message was not sent")
    print("\nTroubleshooting:")
    print("1. Is signal-cli-rest-api running? Check: curl http://localhost:8080/v1/about")
    print(f"2. Is {SENDER_PHONE} registered with Signal?")
    print(f"3. Is {TEST_RECIPIENT} a valid Signal number?")
    print("4. Check the logs above for error details")

print("\n" + "="*60)
print("Test completed")
print("="*60)
