from __future__ import annotations
import streamlit as st

# Full language name map (ISO 639-1 → display name)
LANGUAGE_NAMES = {
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian",
    "bn": "Bengali", "bs": "Bosnian", "bg": "Bulgarian", "ca": "Catalan",
    "ceb": "Cebuano", "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)",
    "co": "Corsican", "hr": "Croatian", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "en": "English", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "fy": "Frisian", "gl": "Galician",
    "ka": "Georgian", "de": "German", "el": "Greek", "gu": "Gujarati",
    "ht": "Haitian Creole", "ha": "Hausa", "haw": "Hawaiian", "he": "Hebrew",
    "hi": "Hindi", "hmn": "Hmong", "hu": "Hungarian", "is": "Icelandic",
    "ig": "Igbo", "id": "Indonesian", "ga": "Irish", "it": "Italian",
    "ja": "Japanese", "jv": "Javanese", "kn": "Kannada", "kk": "Kazakh",
    "km": "Khmer", "rw": "Kinyarwanda", "ko": "Korean", "ku": "Kurdish",
    "ky": "Kyrgyz", "lo": "Lao", "la": "Latin", "lv": "Latvian",
    "lt": "Lithuanian", "lb": "Luxembourgish", "mk": "Macedonian",
    "mg": "Malagasy", "ms": "Malay", "ml": "Malayalam", "mt": "Maltese",
    "mi": "Maori", "mr": "Marathi", "mn": "Mongolian", "my": "Myanmar",
    "ne": "Nepali", "no": "Norwegian", "ny": "Nyanja", "or": "Odia",
    "ps": "Pashto", "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "pa": "Punjabi", "ro": "Romanian", "ru": "Russian", "sm": "Samoan",
    "gd": "Scots Gaelic", "sr": "Serbian", "st": "Sesotho", "sn": "Shona",
    "sd": "Sindhi", "si": "Sinhala", "sk": "Slovak", "sl": "Slovenian",
    "so": "Somali", "es": "Spanish", "su": "Sundanese", "sw": "Swahili",
    "sv": "Swedish", "tl": "Tagalog", "tg": "Tajik", "ta": "Tamil",
    "tt": "Tatar", "te": "Telugu", "th": "Thai", "tr": "Turkish",
    "tk": "Turkmen", "uk": "Ukrainian", "ur": "Urdu", "ug": "Uyghur",
    "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh", "xh": "Xhosa",
    "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu",
}


def detect_language(text: str) -> tuple[str, str]:
    """
    Detect the language of text.
    Returns (lang_code, lang_name).
    Falls back to ('en', 'English') on failure.
    """
    try:
        from langdetect import detect
        code = detect(str(text)[:500])
        name = LANGUAGE_NAMES.get(code, code.upper())
        return code, name
    except Exception:
        return "en", "English"


@st.cache_data(show_spinner=False, ttl=3600)
def translate_to_english(text: str, source_lang: str) -> tuple[str, bool]:
    """
    Translate text to English using Google Translate (via deep-translator).
    Returns (translated_text, was_translated).
    Chunks long text to stay within API limits.
    """
    if source_lang == "en":
        return text, False

    try:
        from deep_translator import GoogleTranslator

        # Split into chunks of 4500 chars (API limit is 5000)
        chunk_size = 4500
        chunks     = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        translated_chunks = []

        for chunk in chunks:
            t = GoogleTranslator(source=source_lang, target="en").translate(chunk)
            translated_chunks.append(t or chunk)

        return " ".join(translated_chunks), True
    except Exception:
        # If translation fails, return original — model will still try
        return text, False


def get_language_flag(lang_code: str) -> str:
    """Return a flag emoji for common languages."""
    flags = {
        "en": "🇬🇧", "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸", "pt": "🇵🇹",
        "it": "🇮🇹", "nl": "🇳🇱", "ru": "🇷🇺", "ar": "🇸🇦", "zh-cn": "🇨🇳",
        "zh-tw": "🇹🇼", "ja": "🇯🇵", "ko": "🇰🇷", "hi": "🇮🇳", "tr": "🇹🇷",
        "pl": "🇵🇱", "sv": "🇸🇪", "da": "🇩🇰", "fi": "🇫🇮", "no": "🇳🇴",
        "cs": "🇨🇿", "ro": "🇷🇴", "hu": "🇭🇺", "uk": "🇺🇦", "el": "🇬🇷",
        "he": "🇮🇱", "fa": "🇮🇷", "id": "🇮🇩", "ms": "🇲🇾", "th": "🇹🇭",
        "vi": "🇻🇳", "sw": "🇰🇪", "yo": "🇳🇬", "ha": "🇳🇬", "am": "🇪🇹",
        "af": "🇿🇦", "zu": "🇿🇦",
    }
    return flags.get(lang_code, "🌐")
