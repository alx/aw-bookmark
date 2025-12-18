#!/usr/bin/env python3
"""
Validation tests for Discord messaging client.
Tests various invalid configuration scenarios.
"""

import logging
from aw_bookmark.messaging.clients.discord import DiscordClient

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_config(name: str, config: dict, should_pass: bool = False):
    """Test a configuration and report results."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    print(f"Config: {config}")

    try:
        client = DiscordClient(config)
        is_valid, error = client.validate_config()

        if should_pass:
            if is_valid:
                print(f"✓ PASS: Config is valid (expected)")
            else:
                print(f"✗ FAIL: Config is invalid but should be valid")
                print(f"  Error: {error}")
        else:
            if not is_valid:
                print(f"✓ PASS: Config is invalid (expected)")
                print(f"  Error: {error}")
            else:
                print(f"✗ FAIL: Config is valid but should be invalid")
    except Exception as e:
        print(f"✗ ERROR: {e}")

# Valid configurations (should pass)
test_config(
    "Valid config with single webhook",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz'
        }
    },
    should_pass=True
)

test_config(
    "Valid config with multiple webhooks",
    {
        'enabled': True,
        'webhook_urls': {
            'work': 'https://discord.com/api/webhooks/1234567890123456789/token_work_xyz',
            'personal': 'https://discord.com/api/webhooks/9876543210987654321/token_personal_abc'
        }
    },
    should_pass=True
)

test_config(
    "Valid config with discordapp.com domain",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discordapp.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz'
        }
    },
    should_pass=True
)

test_config(
    "Valid config with optional fields",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz'
        },
        'message_template': '🔖 **{title}**\n{url}',
        'timeout': 10.0
    },
    should_pass=True
)

# Missing required fields
test_config(
    "Missing webhook_urls",
    {
        'enabled': True
    },
    should_pass=False
)

# Invalid webhook_urls structure
test_config(
    "webhook_urls not a dict",
    {
        'enabled': True,
        'webhook_urls': ['https://discord.com/api/webhooks/123/abc']
    },
    should_pass=False
)

test_config(
    "webhook_url not a string",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 12345
        }
    },
    should_pass=False
)

# Invalid webhook URL formats
test_config(
    "URL with http instead of https",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'http://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz'
        }
    },
    should_pass=False
)

test_config(
    "URL with wrong domain",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://example.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz'
        }
    },
    should_pass=False
)

test_config(
    "URL missing webhook ID",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/'
        }
    },
    should_pass=False
)

test_config(
    "URL missing webhook token",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/1234567890123456789'
        }
    },
    should_pass=False
)

test_config(
    "URL with non-numeric webhook ID",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/abc123xyz/tokenabcdefghij'
        }
    },
    should_pass=False
)

test_config(
    "URL with too-short webhook ID",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/12345/tokenabcdefghij'
        }
    },
    should_pass=False
)

test_config(
    "URL with too-short token",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/1234567890123456789/abc'
        }
    },
    should_pass=False
)

test_config(
    "Empty webhook_urls dict",
    {
        'enabled': True,
        'webhook_urls': {}
    },
    should_pass=True  # Empty dict is technically valid structure-wise
)

test_config(
    "URL with extra path segments (should still be valid)",
    {
        'enabled': True,
        'webhook_urls': {
            'test': 'https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz/extra'
        }
    },
    should_pass=True  # Extra path segments are allowed
)

print(f"\n{'='*60}")
print("Validation tests completed!")
print(f"{'='*60}")
