# aw-bookmark

**Save bookmarks to ActivityWatch with one click!**

aw-bookmark is an HTTP server and Firefox extension that allows you to save web page bookmarks directly to [ActivityWatch](https://activitywatch.net/). Track your bookmarked pages with categories and analyze your browsing patterns.

## Features

- 🔖 **One-click bookmarking** via Firefox extension with emoji category buttons
- 📊 **Track in ActivityWatch** - All bookmarks stored as events in your ActivityWatch database
- 🏷️ **Categorize bookmarks** - Organize with custom categories (toptopbot, education, crypto, etc.)
- 🚀 **Auto-start service** - Run as systemd user service on login
- 🌐 **Bookmarklet support** - Use on sites without CSP restrictions
- 💾 **Local and private** - All data stays on your machine

## How It Works

aw-bookmark runs a local HTTP server (default: `localhost:5601`) that receives bookmark requests and stores them as events in your ActivityWatch instance. Use the Firefox extension for the best experience, or bookmarklets for quick access.

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- ActivityWatch server running on 127.0.0.1:5600

## Installation

1. Clone this repository:
```bash
git clone https://github.com/alx/aw-bookmark.git
cd aw-bookmark
```

2. Install dependencies:
```bash
uv sync
```

## Usage

### Running the Server

**Development mode (with debug output):**
```bash
uv run flask --app src.aw_bookmark.server run --debug --host 127.0.0.1 --port 5601
```

**Production mode:**
```bash
uv run flask --app src.aw_bookmark.server run --host 127.0.0.1 --port 5601
```

**Alternative (using entry point):**
```bash
uv run aw-bookmark
```

### Testing with curl

Send a bookmark to the server:
```bash
curl -X POST http://localhost:5601/bookmark \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "title": "Example Site"}'
```

Expected response:
```json
{"status": "success", "message": "Bookmark stored"}
```

### Using Bookmarklets

A bookmarklet is a bookmark stored in your browser that contains JavaScript code. When clicked, it executes the code on the current page, allowing you to save bookmarks to ActivityWatch with a single click.

#### Prerequisites
- The aw-bookmark server must be running on localhost:5601
- ActivityWatch server must be running

#### Bookmarklet Code

**Option 1: Simple Bookmark (No Category)**

The fastest option - just click to save the current page.

```javascript
javascript:(function(){fetch('http://localhost:5601/bookmark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:window.location.href,title:document.title})}).then(r=>r.json()).then(d=>alert(d.message||'Bookmark saved!')).catch(e=>alert('Error: '+e));})();
```

**Option 2: Prompt for Category**

Prompts you to enter a category each time you bookmark a page.

```javascript
javascript:(function(){const category=prompt('Category (optional):','');const data={url:window.location.href,title:document.title};if(category&&category.trim())data.category=category.trim();fetch('http://localhost:5601/bookmark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json()).then(d=>alert(d.message||'Bookmark saved!')).catch(e=>alert('Error: '+e));})();
```

**Option 3: Hardcoded Category**

Create multiple bookmarklets for different categories (work, personal, etc.). No prompts, just one click. Edit `work` to your desired category.

```javascript
javascript:(function(){const category='work';fetch('http://localhost:5601/bookmark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:window.location.href,title:document.title,category:category})}).then(r=>r.json()).then(d=>alert(d.message||'Bookmark saved!')).catch(e=>alert('Error: '+e));})();
```

#### Installation Instructions

**Firefox:**
1. Show bookmarks toolbar: Right-click menu bar → Bookmarks Toolbar
2. Right-click the bookmarks toolbar → New Bookmark
3. Enter a name (e.g., "Save to AW" or "Bookmark: Work")
4. Paste one of the JavaScript codes above into the URL/Location field
5. Click Save

**Chrome/Edge:**
1. Show bookmarks bar: Ctrl+Shift+B (Cmd+Shift+B on Mac)
2. Right-click bookmarks bar → Add page
3. Enter a name and paste the JavaScript code into the URL field
4. Click Save

**Safari:**
1. Show favorites bar: View → Show Favorites Bar
2. Bookmarks → Edit Bookmarks
3. Create new bookmark, paste code into address field

#### Usage
1. Navigate to any webpage you want to bookmark
2. Click your bookmarklet in the toolbar
3. (If using Option 2) Enter a category or leave blank
4. You'll see a confirmation alert
5. Check ActivityWatch to see your bookmark event

#### Troubleshooting
- **"Failed to fetch" error**: Ensure aw-bookmark server is running on localhost:5601
- **No confirmation appears**: Check browser console (F12) for errors
- **Bookmarklet doesn't work**: Verify you pasted the entire code including `javascript:` prefix
- **CSP/NetworkError on GitHub, Twitter, etc.**: These sites block localhost connections via Content Security Policy. The bookmarklet won't work on sites with strict CSP. Try it on Wikipedia, personal blogs, or other sites without CSP restrictions

### Using the Browser Extension (Firefox)

A browser extension works on all websites (including those with CSP like GitHub) and provides a one-click interface for saving bookmarks.

The Firefox extension is available on addons.mozilla.org: https://addons.mozilla.org/en-US/firefox/addon/aw-bookmark/

#### Installation

1. Open Firefox and go to `about:debugging#/runtime/this-firefox`

2. Click "Load Temporary Add-on"

3. Navigate to the `extension/` directory in your cloned repository and select `manifest.json`

4. The extension icon should appear in your toolbar

#### Usage

1. Navigate to any webpage you want to bookmark
2. Click the extension icon in the toolbar
3. Click one of the emoji buttons for your desired category:
   - 🤖 toptopbot
   - 📚 education
   - ✨ ahbon
   - 😂 permalol
   - 🏛️ politilol
   - 💰 crypto
   - 👤 self
4. The bookmark is saved and the popup closes automatically

#### Permanent Installation

For permanent installation (survives browser restart):

**Option 1: Firefox Developer Edition**
- Use Firefox Developer Edition or Nightly with extended developer mode enabled
- The extension will persist across restarts

**Option 2: Sign and Install**
```bash
cd extension
zip -r ../aw-bookmark-extension.zip .
cd ..
```
Then sign at https://addons.mozilla.org/developers/ and install the signed .xpi file

### Running as a Systemd Service (Auto-start on Login)

To have aw-bookmark start automatically when you log in, you can set it up as a systemd user service.

#### Create the Service File

1. Create the systemd user directory if it doesn't exist:
   ```bash
   mkdir -p ~/.config/systemd/user
   ```

2. Create the service file at `~/.config/systemd/user/aw-bookmark.service`:
   ```ini
   [Unit]
   Description=ActivityWatch Bookmark Server
   Documentation=https://github.com/alx/aw-bookmark
   After=network.target

   [Service]
   Type=simple
   WorkingDirectory=%h/aw-bookmark
   ExecStart=/usr/bin/env bash -c 'cd %h/aw-bookmark && uv run aw-bookmark'
   Restart=on-failure
   RestartSec=10

   [Install]
   WantedBy=default.target
   ```

   **Note**: `%h` expands to your home directory. If you cloned the repository to a different location, update both paths accordingly. You may also need to specify the full path to `uv` (find it with `which uv`).

#### Enable and Start the Service

3. Reload systemd to recognize the new service:
   ```bash
   systemctl --user daemon-reload
   ```

4. Enable the service to start automatically on login:
   ```bash
   systemctl --user enable aw-bookmark.service
   ```

5. Start the service immediately:
   ```bash
   systemctl --user start aw-bookmark.service
   ```

#### Managing the Service

**Check service status:**
```bash
systemctl --user status aw-bookmark.service
```

**View logs:**
```bash
journalctl --user -u aw-bookmark.service -f
```

**Restart the service:**
```bash
systemctl --user restart aw-bookmark.service
```

**Stop the service:**
```bash
systemctl --user stop aw-bookmark.service
```

**Disable auto-start on login:**
```bash
systemctl --user disable aw-bookmark.service
```

#### Troubleshooting

- **Service fails to start**: Check logs with `journalctl --user -u aw-bookmark.service`
- **uv not found**: Ensure uv is in your PATH. You may need to specify the full path to uv in the ExecStart line
- **ActivityWatch not available**: Ensure ActivityWatch is running before aw-bookmark starts. You can add a delay with `ExecStartPre=/bin/sleep 5` in the service file

## API Reference

### POST /bookmark

Store a bookmark event in ActivityWatch.

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
  ```json
  {
    "url": "<bookmark_url>",
    "title": "<bookmark_title>",
    "category": "<optional_category>"
  }
  ```
  - `url` (required): The URL to bookmark
  - `title` (required): The page title or description
  - `category` (optional): Category for organizing bookmarks. Max 100 characters. Allowed: letters, numbers, spaces, `-`, `_`, `/`, `.`

**Response:**
- Success (201): `{"status": "success", "message": "Bookmark stored"}`
- Invalid JSON (400): `{"error": "Invalid JSON"}`
- Missing fields (400): `{"error": "Missing required fields: url and title"}`
- Invalid category (400): `{"error": "Category must be 100 characters or less"}` or `{"error": "Category contains invalid characters..."}`
- Server error (500): `{"error": "Internal server error: ..."}`

**Examples:**
```bash
# Basic bookmark
curl -X POST http://localhost:5601/bookmark \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "title": "Example Site"}'

# With category
curl -X POST http://localhost:5601/bookmark \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org", "title": "Python Docs", "category": "work/documentation"}'
```

## Configuration

Default configuration:
- Listen host: 127.0.0.1
- Listen port: 5601
- ActivityWatch server: 127.0.0.1:5600
- Bucket ID: `aw-bookmark_{hostname}`

**Note**: When running as a systemd service, you can customize the host and port by modifying the `ExecStart` line in the service file to use Flask options:
```bash
ExecStart=/usr/bin/env bash -c 'cd %h/aw-bookmark && uv run flask --app src.aw_bookmark.server run --host 127.0.0.1 --port 5601'
```

## Resources

- [ActivityWatch Documentation](https://docs.activitywatch.net/en/latest/)
- [ActivityWatch Python API](https://docs.activitywatch.net/en/latest/api/python.html)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
