# Signal Messaging Client Setup Guide

This guide explains how to configure and use the Signal messaging client for aw-bookmark.

## Overview

The Signal client sends bookmark notifications via [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api), a REST API wrapper for signal-cli. It supports:

- Category-based routing (different bookmarks to different recipients)
- Individual phone numbers
- Signal group chats
- Mixed recipients (individuals + groups in same category)

## Prerequisites

1. **Docker** installed on your system
2. **Signal account** registered on a phone number
3. **aw-bookmark** with uv installed

## Setup Steps

### 1. Install and Run signal-cli-rest-api

```bash
# Create a directory for Signal configuration
mkdir -p ~/signal-cli-config

# Run the signal-cli-rest-api container
docker run -d \
  --name signal-api \
  -p 8080:8080 \
  -v ~/signal-cli-config:/home/.local/share/signal-cli \
  bbernhard/signal-cli-rest-api:latest

# Verify it's running
curl http://localhost:8080/v1/about
```

### 2. Register Your Signal Account

**Option A: Link to existing Signal account (recommended)**

1. Open Signal app on your phone
2. Go to Settings → Linked Devices → Link New Device
3. Generate QR code:
   ```bash
   curl -X GET "http://localhost:8080/v1/qrcodelink?device_name=aw-bookmark"
   ```
4. Copy the `tsdevice:/?uuid=...` URL from the response
5. Generate and scan QR code or use the URL directly in Signal app

**Option B: Register a new number**

```bash
# Start registration (requires a phone number with SMS/voice capability)
curl -X POST "http://localhost:8080/v1/register/+1234567890"

# Verify with the code received via SMS
curl -X POST "http://localhost:8080/v1/register/+1234567890/verify/123456"
```

### 3. Get Signal Group IDs (if using groups)

```bash
# List all groups for your registered number
curl -X GET "http://localhost:8080/v1/groups/+1234567890"
```

Copy the group IDs (format: `group.xxxxxxxx`) for use in configuration.

### 4. Configure aw-bookmark

Edit your `config.json`:

```json
{
  "messaging": {
    "enabled": true,
    "clients": {
      "signal": {
        "enabled": true,
        "api_url": "http://localhost:8080",
        "sender": "+1234567890",
        "recipients": {
          "work": {
            "individuals": ["+1111111111", "+2222222222"],
            "groups": ["group.work_team_id"]
          },
          "personal": {
            "individuals": ["+3333333333"],
            "groups": []
          }
        },
        "message_template": "🔖 {title}\n{url}",
        "timeout": 10.0
      }
    },
    "category_routing": {
      "work": ["signal"],
      "personal": ["signal"],
      "_default": []
    }
  }
}
```

### 5. Test the Configuration

```bash
# Run validation tests
uv run python test_signal_validation.py

# Run integration test (edit test_signal.py with your phone numbers first)
uv run python test_signal.py
```

### 6. Start aw-bookmark

```bash
uv run aw-bookmark
```

## Configuration Reference

### Signal Client Settings

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | boolean | Yes | false | Enable/disable Signal client |
| `api_url` | string | Yes | - | Base URL for signal-cli-rest-api |
| `sender` | string | Yes | - | Sender's phone number (+1234567890) |
| `recipients` | object | Yes | - | Category-to-recipients mapping |
| `message_template` | string | No | "🔖 {title}\n{url}" | Message format template |
| `timeout` | float | No | 10.0 | HTTP request timeout (seconds) |

### Recipients Structure

Each category in `recipients` can have:

```json
{
  "category_name": {
    "individuals": ["+1234567890", "+9876543210"],
    "groups": ["group.abc123", "group.xyz789"]
  }
}
```

- `individuals`: List of phone numbers in international format (must start with +)
- `groups`: List of Signal group IDs (must start with "group.")
- At least one of `individuals` or `groups` must be present

### Category Routing

In `category_routing`, specify which clients to use for each category:

```json
{
  "category_routing": {
    "work": ["matrix", "signal"],     // Send to both Matrix and Signal
    "personal": ["signal"],            // Send only to Signal
    "education": ["matrix"],           // Send only to Matrix
    "_default": []                     // No default routing
  }
}
```

## Usage

Once configured, bookmarks are automatically sent to Signal when their category matches a routing rule:

```bash
# Example: Send bookmark with category "work"
curl -X POST http://localhost:5600/api/bookmark \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "title": "Interesting Article",
    "category": "work"
  }'
```

The message will be sent to all recipients configured for the "work" category.

## Troubleshooting

### Messages Not Sending

1. **Check signal-cli-rest-api is running:**
   ```bash
   docker ps | grep signal-api
   curl http://localhost:8080/v1/about
   ```

2. **Verify sender is registered:**
   ```bash
   curl http://localhost:8080/v1/accounts
   ```
   Your sender number should appear in the list.

3. **Check aw-bookmark logs:**
   ```bash
   uv run aw-bookmark --debug
   ```
   Look for "Signal" related log messages.

4. **Test manually with curl:**
   ```bash
   curl -X POST http://localhost:8080/v2/send \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Test message",
       "number": "+1234567890",
       "recipients": ["+9999999999"]
     }'
   ```

### Configuration Errors

Run the validation test to check your config:

```bash
uv run python test_signal_validation.py
```

Common errors:
- **Phone numbers must start with +**: Use international format (+1234567890)
- **Group IDs must start with "group."**: Get correct IDs from `/v1/groups` endpoint
- **At least 7 digits required**: Phone numbers must be at least 7 digits (excluding +)

### Docker Container Issues

```bash
# View container logs
docker logs signal-api

# Restart container
docker restart signal-api

# Remove and recreate container
docker rm -f signal-api
# Then run the docker run command again
```

### Permission Denied Errors

```bash
# Fix permissions on signal-cli config directory
chmod -R 755 ~/signal-cli-config
```

## Advanced Configuration

### Multiple Senders

To use different Signal accounts for different categories, you would need to run multiple signal-cli-rest-api instances on different ports and configure separate Signal clients in aw-bookmark.

### Proxy Support

If signal-cli-rest-api needs to go through a proxy:

```bash
docker run -d \
  --name signal-api \
  -p 8080:8080 \
  -e http_proxy=http://proxy.example.com:8080 \
  -e https_proxy=http://proxy.example.com:8080 \
  -v ~/signal-cli-config:/home/.local/share/signal-cli \
  bbernhard/signal-cli-rest-api:latest
```

### Systemd Service

To run signal-cli-rest-api as a systemd service, create `/etc/systemd/system/signal-api.service`:

```ini
[Unit]
Description=Signal CLI REST API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/docker run -d --name signal-api -p 8080:8080 -v /home/user/signal-cli-config:/home/.local/share/signal-cli bbernhard/signal-cli-rest-api:latest
ExecStop=/usr/bin/docker stop signal-api
ExecStopPost=/usr/bin/docker rm signal-api

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl enable signal-api
sudo systemctl start signal-api
```

## Security Considerations

1. **signal-cli-rest-api has no authentication** - Only expose it on localhost or trusted networks
2. **Phone numbers in config.json** - Protect your config file with appropriate permissions (chmod 600)
3. **Signal credentials in Docker volume** - Secure the `~/signal-cli-config` directory
4. **Message content** - Bookmark URLs may contain sensitive information; Signal provides end-to-end encryption

## Resources

- [signal-cli-rest-api Documentation](https://github.com/bbernhard/signal-cli-rest-api)
- [signal-cli GitHub](https://github.com/AsamK/signal-cli)
- [Signal API Endpoint Reference](https://bbernhard.github.io/signal-cli-rest-api/)
- [aw-bookmark Documentation](README.md)
