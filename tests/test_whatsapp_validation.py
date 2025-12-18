#!/usr/bin/env python3
"""
Validation tests for WhatsApp messaging client.
Tests various invalid configuration scenarios.
"""

import logging
from aw_bookmark.messaging.clients.whatsapp import WhatsAppClient

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_config(name: str, config: dict, should_pass: bool = False):
    """Test a configuration and report results."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    print(f"Config: {config}")

    try:
        client = WhatsAppClient(config)
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
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'individuals': ['+1234567890']
            }
        }
    },
    should_pass=True
)

test_config(
    "Valid config with groups",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'groups': ['123456789@g.us']
            }
        }
    },
    should_pass=True
)

test_config(
    "Valid config with both individuals and groups",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'individuals': ['+1234567890', '+9876543210'],
                'groups': ['123456789@g.us', '987654321-1234567890@g.us']
            }
        }
    },
    should_pass=True
)

test_config(
    "Valid config with session",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'session': 'custom-session',
        'recipients': {
            'test': {
                'individuals': ['+1234567890']
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
        'recipients': {}
    },
    should_pass=False
)

test_config(
    "Missing recipients",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000'
    },
    should_pass=False
)

# Invalid recipients structure
test_config(
    "Recipients not a dict",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': ['invalid']
    },
    should_pass=False
)

test_config(
    "Recipient config not a dict",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
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
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'individuals': '+1234567890'
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid phone number in individuals (no + prefix)",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'individuals': ['+1234567890', '9876543210']
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid phone number in individuals (non-digits)",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'individuals': ['+123abc7890']
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid phone number in individuals (too short)",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'individuals': ['+123456']
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
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'groups': '123456789@g.us'
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid group ID format (no @g.us suffix)",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'groups': ['123456789']
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid group ID format (wrong suffix)",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'groups': ['123456789@c.us']
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid group ID format (too short)",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'groups': ['12@g.us']
            }
        }
    },
    should_pass=False
)

test_config(
    "Invalid group ID format (just @g.us)",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'groups': ['@g.us']
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
        'api_url': 'http://localhost:3000',
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
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'individuals': []
            }
        }
    },
    should_pass=True  # Empty lists are allowed, validation only checks structure
)

test_config(
    "Category with empty groups and no individuals",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'test': {
                'groups': []
            }
        }
    },
    should_pass=True  # Empty lists are allowed, validation only checks structure
)

# Multiple categories
test_config(
    "Valid config with multiple categories",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'work': {
                'individuals': ['+1111111111'],
                'groups': ['111111111@g.us']
            },
            'personal': {
                'individuals': ['+2222222222'],
                'groups': []
            },
            'education': {
                'individuals': [],
                'groups': ['222222222@g.us']
            }
        }
    },
    should_pass=True
)

test_config(
    "Multiple categories with one invalid",
    {
        'enabled': True,
        'api_url': 'http://localhost:3000',
        'recipients': {
            'work': {
                'individuals': ['+1111111111']
            },
            'personal': {
                'individuals': ['invalid-phone']
            }
        }
    },
    should_pass=False
)

print(f"\n{'='*60}")
print("Validation tests completed!")
print(f"{'='*60}")
