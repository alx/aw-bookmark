// Default settings
const DEFAULT_SETTINGS = {
  protocol: 'http',
  host: 'localhost',
  port: 5601
};

// Default categories (fallback if not configured)
const DEFAULT_CATEGORIES = [
  { id: "cat_1", emoji: "🤖", label: "toptopbot" },
  { id: "cat_2", emoji: "📚", label: "education" },
  { id: "cat_3", emoji: "✨", label: "ahbon" },
  { id: "cat_4", emoji: "😂", label: "permalol" },
  { id: "cat_5", emoji: "🏛️", label: "politilol" },
  { id: "cat_6", emoji: "💰", label: "crypto" },
  { id: "cat_7", emoji: "👤", label: "self" }
];

// DOM elements
const buttonsContainer = document.getElementById('buttons-container');
const statusDiv = document.getElementById('status');

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  await loadAndRenderCategories();
});

// Load categories from storage and render buttons
async function loadAndRenderCategories() {
  try {
    const result = await browser.storage.sync.get('bookmarkCategories');
    const categories = result.bookmarkCategories || DEFAULT_CATEGORIES;

    renderCategoryButtons(categories);
  } catch (error) {
    console.error('Error loading categories:', error);
    // Fallback to defaults
    renderCategoryButtons(DEFAULT_CATEGORIES);
  }
}

// Render category buttons dynamically
function renderCategoryButtons(categories) {
  buttonsContainer.innerHTML = '';

  categories.forEach(category => {
    const button = document.createElement('button');
    button.className = 'emoji-btn';
    button.dataset.category = category.label;

    const emojiSpan = document.createElement('span');
    emojiSpan.className = 'emoji';
    emojiSpan.textContent = category.emoji;

    const labelSpan = document.createElement('span');
    labelSpan.className = 'label';
    labelSpan.textContent = category.label;

    button.appendChild(emojiSpan);
    button.appendChild(labelSpan);

    // Add click handler
    button.addEventListener('click', async () => {
      await saveBookmark(category.label, button);
    });

    buttonsContainer.appendChild(button);
  });
}

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
