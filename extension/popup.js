// Default settings
const DEFAULT_SETTINGS = {
  protocol: 'http',
  host: 'localhost',
  port: 5601
};

// Get all emoji buttons
const buttons = document.querySelectorAll('.emoji-btn');
const statusDiv = document.getElementById('status');

// Add click handler to each button
buttons.forEach(button => {
  button.addEventListener('click', async () => {
    const category = button.dataset.category;
    await saveBookmark(category, button);
  });
});

// Get server URL from settings
async function getServerUrl() {
  try {
    const result = await browser.storage.sync.get('serverSettings');
    const settings = result.serverSettings || DEFAULT_SETTINGS;
    return `${settings.protocol}://${settings.host}:${settings.port}/bookmark`;
  } catch (error) {
    console.error('Error loading settings, using defaults:', error);
    return 'http://localhost:5601/bookmark';
  }
}

async function saveBookmark(category, button) {
  try {
    // Disable button during save
    button.classList.add('saving');
    button.disabled = true;

    // Get current tab info
    const tabs = await browser.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];

    // Copy URL to clipboard
    await navigator.clipboard.writeText(currentTab.url);

    // Prepare bookmark data
    const bookmarkData = {
      url: currentTab.url,
      title: currentTab.title,
      category: category
    };

    // Get server URL from settings
    const serverUrl = await getServerUrl();

    // Send to aw-bookmark server
    const response = await fetch(serverUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(bookmarkData)
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const result = await response.json();

    // Show success message
    showStatus(`✓ Saved to ${category}`, 'success');

  } catch (error) {
    console.error('Error saving bookmark:', error);
    showStatus(`✗ Error: ${error.message}`, 'error');
  } finally {
    // Re-enable button
    button.classList.remove('saving');
    button.disabled = false;
  }
}

function showStatus(message, type) {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
  statusDiv.classList.remove('hidden');
}
