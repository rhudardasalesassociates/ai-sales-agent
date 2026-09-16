from typing import Dict, Optional


class LanguageDetector:
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "tl": "Tagalog",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "hi": "Hindi",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "ms": "Malaysian",
    }

    COMMON_WORDS = {
        "en": ["the", "is", "are", "what", "how", "can", "you", "help", "buy", "price"],
        "es": ["el", "es", "son", "que", "como", "puedes", "ayudar", "comprar", "precio"],
        "fr": ["le", "est", "sont", "quoi", "comment", "pouvez", "aider", "acheter", "prix"],
        "de": ["der", "ist", "sind", "was", "wie", "können", "helfen", "kaufen", "preis"],
        "tl": ["ang", "ay", "mga", "ano", "paano", "mo", "tulong", "bili", "presyo"],
    }

    @classmethod
    def detect_simple(cls, text: str) -> str:
        text_lower = text.lower()
        words = set(text_lower.split())

        scores = {}
        for lang, common_words in cls.COMMON_WORDS.items():
            score = len(words.intersection(set(common_words)))
            if score > 0:
                scores[lang] = score

        if scores:
            return max(scores, key=scores.get)

        return "en"

    @classmethod
    def get_language_name(cls, code: str) -> str:
        return cls.SUPPORTED_LANGUAGES.get(code, "Unknown")

    @classmethod
    def is_supported(cls, language_code: str) -> bool:
        return language_code in cls.SUPPORTED_LANGUAGES