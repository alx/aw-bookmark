// Default settings
const DEFAULT_SETTINGS = {
  protocol: 'http',
  host: 'localhost',
  port: 5601
};

// Default categories
const DEFAULT_CATEGORIES = [
  { id: "cat_1", emoji: "🤖", label: "toptopbot" },
  { id: "cat_2", emoji: "📚", label: "education" },
  { id: "cat_3", emoji: "✨", label: "ahbon" },
  { id: "cat_4", emoji: "😂", label: "permalol" },
  { id: "cat_5", emoji: "🏛️", label: "politilol" },
  { id: "cat_6", emoji: "💰", label: "crypto" },
  { id: "cat_7", emoji: "👤", label: "self" }
];

// Category management state
let categories = [];
let draggedElement = null;

// DOM elements
const form = document.getElementById('settings-form');
const protocolInput = document.getElementById('protocol');
const hostInput = document.getElementById('host');
const portInput = document.getElementById('port');
const urlDisplay = document.getElementById('url-display');
const statusDiv = document.getElementById('status');
const saveBtn = document.getElementById('save-btn');
const resetBtn = document.getElementById('reset-btn');

// Category DOM elements
const categoriesList = document.getElementById('categories-list');
const newCategoryEmoji = document.getElementById('new-category-emoji');
const newCategoryLabel = document.getElementById('new-category-label');
const addCategoryBtn = document.getElementById('add-category-btn');

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
  await loadCategories();
  setupEventListeners();
});

// Load settings from storage
async function loadSettings() {
  try {
    const result = await browser.storage.sync.get('serverSettings');
    const settings = result.serverSettings || DEFAULT_SETTINGS;

    // Populate form fields
    protocolInput.value = settings.protocol;
    hostInput.value = settings.host;
    portInput.value = settings.port;

    // Update preview
    updateUrlPreview();
  } catch (error) {
    console.error('Error loading settings:', error);
    showStatus('Error loading settings', 'error');
  }
}

// Save settings to storage
async function saveSettings(settings) {
  try {
    await browser.storage.sync.set({ serverSettings: settings });
    showStatus('Settings saved successfully!', 'success');
  } catch (error) {
    console.error('Error saving settings:', error);
    showStatus(`Error saving settings: ${error.message}`, 'error');
    throw error;
  }
}

// Setup event listeners
function setupEventListeners() {
  // Live URL preview update
  protocolInput.addEventListener('change', updateUrlPreview);
  hostInput.addEventListener('input', updateUrlPreview);
  portInput.addEventListener('input', updateUrlPreview);

  // Form submission
  form.addEventListener('submit', handleSubmit);

  // Reset button
  resetBtn.addEventListener('click', handleReset);

  // Category add button
  addCategoryBtn.addEventListener('click', handleAddCategory);
  newCategoryLabel.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      handleAddCategory();
    }
  });
}

// Update URL preview display
function updateUrlPreview() {
  const protocol = protocolInput.value;
  const host = hostInput.value || 'localhost';
  const port = portInput.value || '5601';

  const url = `${protocol}://${host}:${port}/bookmark`;
  urlDisplay.textContent = url;
}

// Handle form submission
async function handleSubmit(e) {
  e.preventDefault();

  // Validate form
  if (!form.checkValidity()) {
    showStatus('Please fix validation errors', 'error');
    return;
  }

  // Additional validation
  const host = hostInput.value.trim();
  const port = parseInt(portInput.value, 10);

  if (!host) {
    showStatus('Host cannot be empty', 'error');
    return;
  }

  if (port < 1 || port > 65535) {
    showStatus('Port must be between 1 and 65535', 'error');
    return;
  }

  // Validate hostname/IP format
  if (!isValidHost(host)) {
    showStatus('Invalid hostname or IP address', 'error');
    return;
  }

  // Save settings
  const settings = {
    protocol: protocolInput.value,
    host: host,
    port: port
  };

  try {
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    await saveSettings(settings);

  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = 'Save Settings';
  }
}

// Handle reset to defaults
async function handleReset() {
  if (confirm('Reset to default settings and categories?')) {
    // Reset server settings
    protocolInput.value = DEFAULT_SETTINGS.protocol;
    hostInput.value = DEFAULT_SETTINGS.host;
    portInput.value = DEFAULT_SETTINGS.port;

    updateUrlPreview();

    // Reset categories
    categories = [...DEFAULT_CATEGORIES];
    renderCategories();

    try {
      await saveSettings(DEFAULT_SETTINGS);
      await saveCategories();
    } catch (error) {
      // Error already shown by save functions
    }
  }
}

// Validate hostname or IP address
function isValidHost(host) {
  // Allow localhost
  if (host === 'localhost') {
    return true;
  }

  // IPv4 pattern
  const ipv4Pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (ipv4Pattern.test(host)) {
    // Check each octet is 0-255
    const octets = host.split('.');
    return octets.every(octet => {
      const num = parseInt(octet, 10);
      return num >= 0 && num <= 255;
    });
  }

  // Hostname pattern (RFC 1123)
  const hostnamePattern = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  return hostnamePattern.test(host);
}

// Show status message
function showStatus(message, type) {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
  statusDiv.classList.remove('hidden');

  // Auto-hide success messages after 3 seconds
  if (type === 'success') {
    setTimeout(() => {
      statusDiv.classList.add('hidden');
    }, 3000);
  }
}

// Category Management Functions

// Load categories from storage
async function loadCategories() {
  try {
    const result = await browser.storage.sync.get('bookmarkCategories');
    categories = result.bookmarkCategories || DEFAULT_CATEGORIES;

    // If no categories in storage, save defaults
    if (!result.bookmarkCategories) {
      await saveCategories();
    }

    renderCategories();
  } catch (error) {
    console.error('Error loading categories:', error);
    showStatus('Error loading categories', 'error');
    categories = DEFAULT_CATEGORIES;
    renderCategories();
  }
}

// Save categories to storage
async function saveCategories() {
  try {
    await browser.storage.sync.set({ bookmarkCategories: categories });
    showStatus('Categories saved successfully!', 'success');
  } catch (error) {
    console.error('Error saving categories:', error);
    showStatus(`Error saving categories: ${error.message}`, 'error');
    throw error;
  }
}

// Render categories list
function renderCategories() {
  categoriesList.innerHTML = '';

  categories.forEach((category, index) => {
    const item = createCategoryItem(category, index);
    categoriesList.appendChild(item);
  });
}

// Create a single category item element
function createCategoryItem(category, index) {
  const item = document.createElement('div');
  item.className = 'category-item';
  item.draggable = true;
  item.dataset.categoryId = category.id;
  item.dataset.index = index;

  // Drag handle
  const dragHandle = document.createElement('span');
  dragHandle.className = 'drag-handle';
  dragHandle.textContent = '☰';
  dragHandle.title = 'Drag to reorder';

  // Category content
  const content = document.createElement('div');
  content.className = 'category-content';

  const emoji = document.createElement('span');
  emoji.className = 'category-emoji';
  emoji.textContent = category.emoji;
  emoji.contentEditable = true;
  emoji.dataset.categoryId = category.id;
  emoji.dataset.field = 'emoji';
  emoji.title = 'Click to edit emoji';

  const label = document.createElement('input');
  label.type = 'text';
  label.className = 'category-label';
  label.value = category.label;
  label.dataset.categoryId = category.id;
  label.dataset.field = 'label';
  label.placeholder = 'Category name';

  content.appendChild(emoji);
  content.appendChild(label);

  // Delete button
  const deleteBtn = document.createElement('button');
  deleteBtn.type = 'button';
  deleteBtn.className = 'delete-btn';
  deleteBtn.textContent = '🗑️';
  deleteBtn.title = 'Delete category';
  deleteBtn.dataset.categoryId = category.id;

  // Assemble item
  item.appendChild(dragHandle);
  item.appendChild(content);
  item.appendChild(deleteBtn);

  // Add event listeners
  setupCategoryItemListeners(item, emoji, label, deleteBtn);

  return item;
}

// Setup event listeners for category items
function setupCategoryItemListeners(item, emoji, label, deleteBtn) {
  // Drag events
  item.addEventListener('dragstart', handleDragStart);
  item.addEventListener('dragend', handleDragEnd);
  item.addEventListener('dragover', handleDragOver);
  item.addEventListener('drop', handleDrop);
  item.addEventListener('dragleave', handleDragLeave);

  // Edit events
  emoji.addEventListener('blur', handleEmojiEdit);
  emoji.addEventListener('keydown', handleEmojiKeydown);
  emoji.addEventListener('paste', handleEmojiPaste);

  label.addEventListener('blur', handleLabelEdit);
  label.addEventListener('keydown', handleLabelKeydown);

  // Delete event
  deleteBtn.addEventListener('click', handleDelete);
}

// Drag and drop handlers
function handleDragStart(e) {
  draggedElement = e.currentTarget;
  e.currentTarget.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/html', e.currentTarget.innerHTML);
}

function handleDragEnd(e) {
  e.currentTarget.classList.remove('dragging');

  // Remove drag-over class from all items
  document.querySelectorAll('.category-item').forEach(item => {
    item.classList.remove('drag-over');
  });

  draggedElement = null;
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault();
  }

  e.dataTransfer.dropEffect = 'move';

  const target = e.currentTarget;
  if (target !== draggedElement) {
    target.classList.add('drag-over');
  }

  return false;
}

function handleDragLeave(e) {
  e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
  if (e.stopPropagation) {
    e.stopPropagation();
  }

  e.preventDefault();

  const target = e.currentTarget;
  target.classList.remove('drag-over');

  if (draggedElement !== target) {
    const draggedIndex = parseInt(draggedElement.dataset.index);
    const targetIndex = parseInt(target.dataset.index);

    // Reorder categories array
    const [movedCategory] = categories.splice(draggedIndex, 1);
    categories.splice(targetIndex, 0, movedCategory);

    // Re-render and save
    renderCategories();
    saveCategories();
  }

  return false;
}

// Edit handlers
function handleEmojiEdit(e) {
  const categoryId = e.target.dataset.categoryId;
  const newEmoji = e.target.textContent.trim();

  if (newEmoji.length === 0) {
    showStatus('Emoji cannot be empty', 'error');
    renderCategories(); // Reset to original
    return;
  }

  // Limit to 2 characters (handles complex emojis)
  if (newEmoji.length > 2) {
    e.target.textContent = newEmoji.substring(0, 2);
    return;
  }

  updateCategory(categoryId, 'emoji', newEmoji);
}

function handleEmojiKeydown(e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    e.target.blur();
  }
}

function handleEmojiPaste(e) {
  e.preventDefault();
  const text = e.clipboardData.getData('text/plain').substring(0, 2);
  document.execCommand('insertText', false, text);
}

function handleLabelEdit(e) {
  const categoryId = e.target.dataset.categoryId;
  const newLabel = e.target.value.trim();

  if (newLabel.length === 0) {
    showStatus('Label cannot be empty', 'error');
    renderCategories(); // Reset to original
    return;
  }

  updateCategory(categoryId, 'label', newLabel);
}

function handleLabelKeydown(e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    e.target.blur();
  }
}

// Update category in array and save
function updateCategory(categoryId, field, value) {
  const category = categories.find(cat => cat.id === categoryId);
  if (category) {
    category[field] = value;
    saveCategories();
  }
}

// Add new category
function handleAddCategory() {
  const emoji = newCategoryEmoji.value.trim();
  const label = newCategoryLabel.value.trim();

  if (!emoji || !label) {
    showStatus('Please enter both emoji and label', 'error');
    return;
  }

  // Generate unique ID using timestamp
  const id = `cat_${Date.now()}`;

  const newCategory = { id, emoji, label };
  categories.push(newCategory);

  // Clear inputs
  newCategoryEmoji.value = '';
  newCategoryLabel.value = '';

  // Re-render and save
  renderCategories();
  saveCategories();

  // Focus back to emoji input for easy sequential adding
  newCategoryEmoji.focus();
}

// Delete category
function handleDelete(e) {
  const categoryId = e.currentTarget.dataset.categoryId;
  const category = categories.find(cat => cat.id === categoryId);

  if (!category) return;

  if (confirm(`Delete category "${category.label}"?`)) {
    categories = categories.filter(cat => cat.id !== categoryId);
    renderCategories();
    saveCategories();
  }
}
