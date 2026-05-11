# NetConfirm Browser Extension

Instantly check any news article for misinformation directly from your browser.

## Supported Browsers
- ✅ Chrome / Chromium
- ✅ Microsoft Edge
- ✅ Firefox (109+)

---

## Install on Chrome / Edge

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer Mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `extension/` folder from this project
5. The NetConfirm icon will appear in your toolbar

---

## Install on Firefox

1. Open Firefox and go to `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Select `extension/manifest.json`
4. The extension loads until Firefox restarts

For permanent install, package it:
```bash
cd extension
zip -r netconfirm-extension.zip .
```
Then submit to Firefox Add-ons or load via `about:addons`.

---

## Setup

1. Click the NetConfirm icon in your toolbar
2. Click ⚙️ Settings
3. Enter your **API Key** (get one from the NetConfirm app → ⚡ API tab)
4. Set your **API Base URL** (your Render API service URL)
5. Click **Save Settings**

---

## Usage

1. Navigate to any news article
2. Click the NetConfirm extension icon
3. Click **🔍 Analyse This Page**
4. See the verdict instantly — FAKE or REAL with confidence score, gauge, and signal breakdown
5. Click **↗ Open Full Analysis** to see SHAP explanations in the full app

---

## Features

- 🔍 Auto-extracts article text from any news page
- 🌐 Detects language — shows badge if translated
- 📊 Confidence gauge + signal breakdown in the popup
- ⚙️ Configurable API key, API URL, and app URL
- 🔒 API key stored securely in `chrome.storage.sync`
