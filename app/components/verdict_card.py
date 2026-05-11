import io
from PIL import Image, ImageDraw, ImageFont


# ── Colours ────────────────────────────────────────────────
BG        = (15,  23,  42)   # #0f172a
CARD      = (30,  41,  59)   # #1e293b
BORDER    = (51,  65,  85)   # #334155
WHITE     = (241, 245, 249)  # #f1f5f9
SUB       = (148, 163, 184)  # #94a3b8
RED       = (220,  38,  38)  # #dc2626
GREEN     = (22,  163,  74)  # #16a34a
AMBER     = (234, 179,   8)  # #eab308
ORANGE    = (249, 115,  22)  # #f97316
ACCENT    = (26,  26,  46)   # #1a1a2e

W, H = 800, 460


def _font(size: int, bold: bool = False):
    """Return a PIL font — falls back to default if no TTF available."""
    try:
        name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(name, size)
    except Exception:
        try:
            import os
            paths = [
                f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans{}-Bold.ttf".format("" if not bold else ""),
                "/usr/share/fonts/truetype/liberation/LiberationSans{}-Regular.ttf".format("-Bold" if bold else ""),
            ]
            for p in paths:
                if os.path.exists(p):
                    return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                            outline=outline, width=width)


def _gauge_bar(draw: ImageDraw.ImageDraw, x, y, bar_w, bar_h, score: float, color):
    """Draw a horizontal gauge bar."""
    _rounded_rect(draw, [x, y, x + bar_w, y + bar_h], radius=bar_h // 2, fill=BORDER)
    fill_w = max(bar_h, int(bar_w * score))
    _rounded_rect(draw, [x, y, x + fill_w, y + bar_h], radius=bar_h // 2, fill=color)


def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw):
    """Wrap text to fit within max_width pixels."""
    words  = text.split()
    lines  = []
    line   = ""
    for word in words:
        test = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and line:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines


def generate_verdict_card(
    verdict: str,
    confidence: float,
    real_prob: float,
    fake_prob: float,
    sentiment: float,
    title: str = "",
    snippet: str = "",
) -> bytes:
    """
    Generate a 800×460 PNG verdict card.
    Returns raw PNG bytes ready for st.download_button.
    """
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    is_fake   = verdict == "FAKE"
    v_color   = RED if is_fake else GREEN
    score_pct = round(real_prob * 100, 1)

    if score_pct >= 75:
        gauge_color, gauge_label = GREEN,  "Likely Authentic"
    elif score_pct >= 50:
        gauge_color, gauge_label = AMBER,  "Uncertain"
    elif score_pct >= 25:
        gauge_color, gauge_label = ORANGE, "Likely Fake"
    else:
        gauge_color, gauge_label = RED,    "High Risk"

    # ── Left accent bar ────────────────────────────────────
    draw.rectangle([0, 0, 6, H], fill=v_color)

    # ── Header band ────────────────────────────────────────
    draw.rectangle([0, 0, W, 70], fill=ACCENT)
    draw.rectangle([0, 68, W, 70], fill=BORDER)

    # Brand icon background
    _rounded_rect(draw, [20, 14, 54, 54], radius=8, fill=v_color)
    draw.text((28, 20), "NC", font=_font(18, bold=True), fill=WHITE)

    # Brand name
    draw.text((64, 16), "NetConfirm", font=_font(18, bold=True), fill=WHITE)
    draw.text((64, 40), "AI Fake News Detector", font=_font(11), fill=SUB)

    # Timestamp
    from datetime import datetime
    ts = datetime.now().strftime("%b %d, %Y  %H:%M")
    ts_bbox = draw.textbbox((0, 0), ts, font=_font(11))
    draw.text((W - ts_bbox[2] - 24, 28), ts, font=_font(11), fill=SUB)

    # ── Verdict badge ──────────────────────────────────────
    badge_x, badge_y = 24, 90
    badge_w = 220
    _rounded_rect(draw, [badge_x, badge_y, badge_x + badge_w, badge_y + 80],
                  radius=12, fill=CARD, outline=v_color, width=2)

    icon = "⚠" if is_fake else "✓"
    draw.text((badge_x + 16, badge_y + 10), icon, font=_font(28, bold=True), fill=v_color)
    draw.text((badge_x + 56, badge_y + 12), verdict, font=_font(28, bold=True), fill=v_color)
    draw.text((badge_x + 16, badge_y + 50), f"{confidence*100:.1f}% confidence",
              font=_font(13), fill=SUB)

    # ── Authenticity score ─────────────────────────────────
    score_x = badge_x
    score_y = badge_y + 100

    draw.text((score_x, score_y), "Authenticity Score", font=_font(12), fill=SUB)
    draw.text((score_x, score_y + 18), f"{score_pct}%", font=_font(32, bold=True), fill=gauge_color)
    draw.text((score_x, score_y + 56), gauge_label, font=_font(12), fill=gauge_color)

    _gauge_bar(draw, score_x, score_y + 76, badge_w, 10, real_prob, gauge_color)

    # ── Signal bars ────────────────────────────────────────
    sig_x = badge_x + badge_w + 24
    sig_y = 90
    sig_w = W - sig_x - 24

    _rounded_rect(draw, [sig_x, sig_y, W - 16, sig_y + 270],
                  radius=12, fill=CARD, outline=BORDER, width=1)

    draw.text((sig_x + 16, sig_y + 14), "SIGNAL BREAKDOWN",
              font=_font(10, bold=True), fill=SUB)

    signals = [
        ("Fake Probability",  fake_prob,  RED),
        ("Real Probability",  real_prob,  GREEN),
        ("Source Sentiment",  sentiment,  (139, 92, 246)),
    ]
    for i, (label, val, color) in enumerate(signals):
        sy = sig_y + 44 + i * 62
        draw.text((sig_x + 16, sy), label, font=_font(11), fill=SUB)
        val_str = f"{val:.3f}"
        vb = draw.textbbox((0, 0), val_str, font=_font(11, bold=True))
        draw.text((W - 16 - vb[2], sy), val_str, font=_font(11, bold=True), fill=WHITE)
        _gauge_bar(draw, sig_x + 16, sy + 18, sig_w - 32, 8, float(val), color)

    # ── Article info ───────────────────────────────────────
    info_y = 380
    draw.rectangle([0, info_y - 1, W, info_y], fill=BORDER)
    _rounded_rect(draw, [16, info_y + 10, W - 16, H - 16],
                  radius=10, fill=CARD, outline=BORDER, width=1)

    content = title if title else snippet
    if content:
        lines = _wrap_text(content[:120], _font(12), W - 80, draw)
        for j, line in enumerate(lines[:2]):
            draw.text((30, info_y + 22 + j * 18), line, font=_font(12), fill=WHITE)

    # Watermark
    wm = "Verified by NetConfirm · netconfirm.app"
    wm_bbox = draw.textbbox((0, 0), wm, font=_font(10))
    draw.text((W - wm_bbox[2] - 20, H - 28), wm, font=_font(10), fill=BORDER)

    # ── Export ─────────────────────────────────────────────
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.getvalue()
