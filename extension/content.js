// content.js — runs on every page, extracts article text on request

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action !== "extractText") return;

  try {
    const text  = extractArticleText();
    const title = document.title || "";
    const url   = window.location.href;
    sendResponse({ text, title, url, ok: true });
  } catch (e) {
    sendResponse({ text: "", title: "", url: window.location.href, ok: false, error: e.message });
  }

  return true; // keep channel open for async
});


function extractArticleText() {
  // Priority order: article tag → main → largest text block → body
  const selectors = [
    "article",
    "[role='main']",
    "main",
    ".article-body",
    ".post-content",
    ".entry-content",
    ".story-body",
    ".article-content",
    "#article-body",
    "#content",
  ];

  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) {
      const t = cleanText(el.innerText);
      if (t.length >= 100) return t;
    }
  }

  // Fallback: find the <p> tags with the most combined text
  const paragraphs = Array.from(document.querySelectorAll("p"));
  const combined   = paragraphs
    .map(p => p.innerText.trim())
    .filter(t => t.length > 40)
    .join(" ");

  if (combined.length >= 100) return cleanText(combined);

  // Last resort: body text
  return cleanText(document.body.innerText).slice(0, 5000);
}


function cleanText(raw) {
  return raw
    .replace(/\s+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim()
    .slice(0, 8000);
}
