// Default settings
const DEFAULT_SETTINGS = {
  protocol: 'http',
  host: 'localhost',
  port: 5601
};

// DOM elements
const form = document.getElementById('settings-form');
const protocolInput = document.getElementById('protocol');
const hostInput = document.getElementById('host');
const portInput = document.getElementById('port');
const urlDisplay = document.getElementById('url-display');
const statusDiv = document.getElementById('status');
const saveBtn = document.getElementById('save-btn');
const resetBtn = document.getElementById('reset-btn');

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
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
  if (confirm('Reset to default settings (http://localhost:5601)?')) {
    protocolInput.value = DEFAULT_SETTINGS.protocol;
    hostInput.value = DEFAULT_SETTINGS.host;
    portInput.value = DEFAULT_SETTINGS.port;

    updateUrlPreview();

    try {
      await saveSettings(DEFAULT_SETTINGS);
    } catch (error) {
      // Error already shown by saveSettings
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
