from flask import Flask, request, jsonify
from aw_client import ActivityWatchClient
from aw_core.models import Event
from datetime import datetime, timezone

app = Flask(__name__)


# Add CORS headers to all responses (needed for bookmarklets)
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Initialize ActivityWatch client
client = ActivityWatchClient("aw-bookmark", testing=False)
bucket_id = f"aw-bookmark_{client.client_hostname}"

# Create bucket on startup (idempotent operation)
try:
    client.create_bucket(bucket_id, event_type="bookmark")
except Exception as e:
    print(f"Warning: Could not create bucket: {e}")


def validate_category(category):
    """Validate category field. Returns (is_valid, error_message)."""
    if not category or not category.strip():
        return True, None  # Empty is valid (optional)

    category = category.strip()

    if len(category) > 100:
        return False, "Category must be 100 characters or less"

    import re
    if not re.match(r'^[a-zA-Z0-9 _/\-\.]+$', category):
        return False, "Category contains invalid characters. Allowed: letters, numbers, spaces, -, _, /, ."

    return True, None


@app.route('/bookmark', methods=['POST', 'OPTIONS'])
def bookmark():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return '', 200

    """
    Accept bookmark POST requests and store them in ActivityWatch.

    Expected JSON format: {"url": "...", "title": "...", "category": "..."} (category optional)
    """
    try:
        # Parse JSON data
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        if 'url' not in data or 'title' not in data:
            return jsonify({'error': 'Missing required fields: url and title'}), 400

        # Validate optional category field
        if 'category' in data:
            is_valid, error_msg = validate_category(data['category'])
            if not is_valid:
                return jsonify({'error': error_msg}), 400

        # Prepare event data
        event_data = {
            'url': data['url'],
            'title': data['title']
        }

        # Add category if provided and not empty
        if 'category' in data and data['category'].strip():
            event_data['category'] = data['category'].strip()

        # Create and insert event
        event = Event(
            timestamp=datetime.now(timezone.utc),
            data=event_data
        )

        client.insert_event(bucket_id, event)

        return jsonify({'status': 'success', 'message': 'Bookmark stored'}), 201

    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


def main():
    """Run the Flask application."""
    app.run(host='127.0.0.1', port=5601)


if __name__ == '__main__':
    main()
