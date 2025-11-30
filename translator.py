import re
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

def translate_text(text, target_lang="zh"):
    """
    Simple translation using a public API (e.g., Google Translate via unauthorized endpoint or similar free tier).
    For production/stability, use a proper API key (Google Cloud, DeepL, etc.).
    Here we use a lightweight trick or a library if available.
    Since we can't easily install heavy translation libs in serverless without size issues,
    let's try a simple google translate scraping method or a very lightweight library.
    
    Actually, 'googletrans' is unstable.
    Let's use a simple mocked translation for now OR try to use a public endpoint if possible.
    
    Better approach for Vercel/Python:
    Use `deep_translator` if we can install it, it wraps multiple translators.
    """
    if not text:
        return ""
        
    # Fallback: just return original if translation fails
    return text

# We will use deep-translator
try:
    from deep_translator import GoogleTranslator
    def translate_text_real(text, target_lang="zh-CN"):
        if not text:
            return ""
        try:
            # Split text if too long (Google limit is around 5000 chars)
            if len(text) > 4500:
                text = text[:4500]
            
            translator = GoogleTranslator(source='auto', target=target_lang)
            return translator.translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text
except ImportError:
    print("deep_translator not found. Install it via pip.")
    translate_text_real = translate_text

