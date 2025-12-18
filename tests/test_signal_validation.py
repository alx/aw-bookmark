#!/usr/bin/env python3
"""
Validation tests for Signal messaging client.
Tests various invalid configuration scenarios.
"""

import logging
from aw_bookmark.messaging.clients.signal import SignalClient

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_config(name: str, config: dict, should_pass: bool = False):
    """Test a configuration and report results."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    print(f"Config: {config}")

    try:
        client = SignalClient(config)
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

# Valid configuration (should pass)
test_config(
    "Valid config with individuals",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'individuals': ['+9999999999']
            }
        }
    },
    should_pass=True
)

test_config(
    "Valid config with groups",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'groups': ['group.abc123xyz']
            }
        }
    },
    should_pass=True
)

test_config(
    "Valid config with both individuals and groups",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'individuals': ['+9999999999', '+8888888888'],
                'groups': ['group.abc123xyz']
            }
        }
    },
    should_pass=True
)

# Missing required fields
test_config(
    "Missing api_url",
    {
        'enabled': True,
        'sender': '+1234567890',
        'recipients': {}
    },
    should_pass=False
)

test_config(
    "Missing sender",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'recipients': {}
    },
    should_pass=False
)

test_config(
    "Missing recipients",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890'
    },
    should_pass=False
)

# Invalid sender phone format
test_config(
    "Sender without + prefix",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '1234567890',
        'recipients': {}
    },
    should_pass=False
)

test_config(
    "Sender with non-digits",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+123abc7890',
        'recipients': {}
    },
    should_pass=False
)

test_config(
    "Sender too short",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+123456',
        'recipients': {}
    },
    should_pass=False
)

# Invalid recipients structure
test_config(
    "Recipients not a dict",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': ['invalid']
    },
    should_pass=False
)

test_config(
    "Recipient config not a dict",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': 'invalid'
        }
    },
    should_pass=False
)

# Invalid individuals list
test_config(
    "Individuals not a list",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'individuals': '+9999999999'
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid phone number in individuals",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'individuals': ['+9999999999', '8888888888']
            }
        }
    },
    should_pass=False
)

# Invalid groups list
test_config(
    "Groups not a list",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'groups': 'group.abc123'
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid group ID format (no prefix)",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'groups': ['abc123xyz']
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid group ID format (too short)",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'groups': ['group.']
            }
        }
    },
    should_pass=False
)

# Missing both individuals and groups
test_config(
    "Category with neither individuals nor groups",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {}
        }
    },
    should_pass=False
)

test_config(
    "Category with empty individuals and no groups",
    {
        'enabled': True,
        'api_url': 'http://localhost:8080',
        'sender': '+1234567890',
        'recipients': {
            'test': {
                'individuals': []
            }
        }
    },
    should_pass=True  # Empty lists are allowed, validation only checks structure
)

print(f"\n{'='*60}")
print("Validation tests completed!")
print(f"{'='*60}")
