// popup.js

const APP_URL_DEFAULT = "https://netconfirm.onrender.com";
const API_URL_DEFAULT = "https://netconfirm-api.onrender.com";

// ── DOM refs ──────────────────────────────────────────────
const pageUrlEl    = document.getElementById("pageUrl");
const analyseBtn   = document.getElementById("analyseBtn");
const loadingBox   = document.getElementById("loadingBox");
const loadingText  = document.getElementById("loadingText");
const errorBox     = document.getElementById("errorBox");
const resultBox    = document.getElementById("resultBox");
const noKeyBox     = document.getElementById("noKeyBox");
const settingsBtn  = document.getElementById("settingsBtn");
const goSettings   = document.getElementById("goSettings");
const openAppBtn   = document.getElementById("openAppBtn");
const langBadge    = document.getElementById("langBadge");

// Result elements
const verdictBanner = document.getElementById("verdictBanner");
const verdictIcon   = document.getElementById("verdictIcon");
const verdictLabel  = document.getElementById("verdictLabel");
const verdictConf   = document.getElementById("verdictConf");
const gaugeVal      = document.getElementById("gaugeVal");
const gaugeFill     = document.getElementById("gaugeFill");
const signalsBox    = document.getElementById("signalsBox");

let currentTab = null;
let appUrl     = APP_URL_DEFAULT;
let apiUrl     = API_URL_DEFAULT;
let apiKey     = "";


// ── Init ──────────────────────────────────────────────────
async function init() {
  // Load settings
  const stored = await chrome.storage.sync.get(["apiKey", "apiUrl", "appUrl"]);
  apiKey = stored.apiKey || "";
  apiUrl = stored.apiUrl || API_URL_DEFAULT;
  appUrl = stored.appUrl || APP_URL_DEFAULT;

  // Get current tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tab;
  pageUrlEl.textContent = tab.url || "Unknown";

  // Show no-key warning if needed
  if (!apiKey) {
    noKeyBox.style.display = "block";
    analyseBtn.disabled = true;
  }

  openAppBtn.onclick = () => chrome.tabs.create({ url: appUrl });
}


// ── Settings ──────────────────────────────────────────────
settingsBtn.onclick = () => chrome.runtime.openOptionsPage();
goSettings.onclick  = () => chrome.runtime.openOptionsPage();


// ── Analyse ───────────────────────────────────────────────
analyseBtn.onclick = async () => {
  show("loading");
  setLoadingText("Extracting article text...");

  try {
    // 1. Extract text from page via content script
    let extracted;
    try {
      extracted = await chrome.tabs.sendMessage(currentTab.id, { action: "extractText" });
    } catch {
      // Content script not injected yet — inject it
      await chrome.scripting.executeScript({
        target: { tabId: currentTab.id },
        files: ["content.js"],
      });
      extracted = await chrome.tabs.sendMessage(currentTab.id, { action: "extractText" });
    }

    if (!extracted || !extracted.text || extracted.text.length < 20) {
      throw new Error("Could not extract enough text from this page. Try a news article page.");
    }

    setLoadingText("Analysing with NetConfirm AI...");

    // 2. Call API
    const response = await fetch(`${apiUrl}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({
        text:           extracted.text,
        trust_score:    0.5,
        follower_count: 1000,
        account_age:    365,
        source_url:     currentTab.url,
      }),
    });

    if (response.status === 401 || response.status === 403) {
      throw new Error("Invalid API key. Go to Settings and check your key.");
    }
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `API error ${response.status}`);
    }

    const data = await response.json();
    renderResult(data, extracted.title || currentTab.title || "");

  } catch (e) {
    showError(e.message);
  }
};


// ── Render result ─────────────────────────────────────────
function renderResult(data, title) {
  const isFake   = data.prediction === "FAKE";
  const confPct  = Math.round(data.confidence * 100);
  const realPct  = Math.round(data.real_prob * 100);
  const fakePct  = Math.round(data.fake_prob * 100);

  // Verdict banner
  verdictBanner.className = `verdict-banner ${isFake ? "fake" : "real"}`;
  verdictIcon.textContent  = isFake ? "⚠️" : "✅";
  verdictLabel.className   = `verdict-label ${isFake ? "fake" : "real"}`;
  verdictLabel.textContent = data.prediction;
  verdictConf.textContent  = `${confPct}% confidence · ${isFake ? "Likely misinformation" : "Appears authentic"}`;

  // Gauge
  const gaugeColor = realPct >= 75 ? "#16a34a" : realPct >= 50 ? "#eab308" : realPct >= 25 ? "#f97316" : "#dc2626";
  gaugeVal.textContent      = `${realPct}%`;
  gaugeFill.style.width     = `${realPct}%`;
  gaugeFill.style.background = gaugeColor;

  // Language badge
  if (data.translated) {
    langBadge.style.display = "inline-flex";
    langBadge.textContent   = `🌐 ${data.language} → translated to English`;
  } else {
    langBadge.style.display = "none";
  }

  // Signal bars
  const signals = [
    { label: "Fake Prob",  val: data.fake_prob,  color: "#dc2626" },
    { label: "Real Prob",  val: data.real_prob,  color: "#16a34a" },
    { label: "Sentiment",  val: data.sentiment,  color: "#8b5cf6" },
    { label: "Readability",val: data.readability, color: "#f59e0b" },
  ];

  signalsBox.innerHTML = signals.map(s => `
    <div class="signal-row">
      <span class="signal-label">${s.label}</span>
      <div class="signal-bar-wrap">
        <div class="signal-bar" style="width:${Math.round(s.val*100)}%;background:${s.color};"></div>
      </div>
      <span class="signal-val">${s.val.toFixed(3)}</span>
    </div>
  `).join("");

  show("result");
}


// ── Helpers ───────────────────────────────────────────────
function show(view) {
  analyseBtn.style.display  = view === "idle"    ? "block"  : "none";
  loadingBox.style.display  = view === "loading" ? "flex"   : "none";
  errorBox.style.display    = view === "error"   ? "block"  : "none";
  resultBox.style.display   = view === "result"  ? "block"  : "none";
  if (view !== "error") errorBox.textContent = "";
}

function showError(msg) {
  errorBox.textContent = `❌ ${msg}`;
  errorBox.style.display = "block";
  loadingBox.style.display = "none";
  analyseBtn.style.display = "block";
}

function setLoadingText(msg) {
  loadingText.textContent = msg;
}


// ── Boot ──────────────────────────────────────────────────
init();
