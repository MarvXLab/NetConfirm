// options.js

const API_URL_DEFAULT = "https://netconfirm-api.onrender.com";
const APP_URL_DEFAULT = "https://netconfirm.onrender.com";

const apiKeyInput = document.getElementById("apiKey");
const apiUrlInput = document.getElementById("apiUrl");
const appUrlInput = document.getElementById("appUrl");
const saveBtn     = document.getElementById("saveBtn");
const toast       = document.getElementById("toast");
const openAppLink = document.getElementById("openApp");


// Load saved settings
chrome.storage.sync.get(["apiKey", "apiUrl", "appUrl"], (stored) => {
  apiKeyInput.value = stored.apiKey || "";
  apiUrlInput.value = stored.apiUrl || API_URL_DEFAULT;
  appUrlInput.value = stored.appUrl || APP_URL_DEFAULT;
});


// Save settings
saveBtn.onclick = () => {
  const apiKey = apiKeyInput.value.trim();
  const apiUrl = apiUrlInput.value.trim() || API_URL_DEFAULT;
  const appUrl = appUrlInput.value.trim() || APP_URL_DEFAULT;

  chrome.storage.sync.set({ apiKey, apiUrl, appUrl }, () => {
    toast.style.display = "block";
    setTimeout(() => { toast.style.display = "none"; }, 3000);
  });
};


// Open app
openAppLink.onclick = (e) => {
  e.preventDefault();
  const appUrl = appUrlInput.value.trim() || APP_URL_DEFAULT;
  chrome.tabs.create({ url: `${appUrl}` });
};
