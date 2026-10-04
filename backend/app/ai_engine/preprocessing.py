import re
import unicodedata
from typing import List, Dict, Any

class TextPreprocessor:
    def __init__(self):
        self.stop_words = {
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
            "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
            "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
            "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
            "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i",
            "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most",
            "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
            "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
            "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
            "themselves", "then", "there", "these", "they", "this", "those", "through", "to",
            "too", "under", "until", "up", "very", "was", "we", "were", "what", "when",
            "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your"
        }

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Unicode normalization
        text = unicodedata.normalize("NFKD", text)
        # Remove multiple newlines and carriage returns
        text = re.sub(r"[\r\n]+", "\n", text)
        # Remove irregular whitespace
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def tokenize_sentences(self, text: str) -> List[str]:
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
        # Split by sentence end punctuation followed by space or newline
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        filtered = [s.strip() for s in sentences if len(s.strip()) > 10]
        return filtered if filtered else [cleaned]

    def tokenize_words(self, text: str) -> List[str]:
        words = re.findall(r"\b[A-Za-z0-9\'-]+\b", text.lower())
        return words

    def extract_keywords(self, text: str, top_n: int = 8) -> List[str]:
        words = self.tokenize_words(text)
        freq: Dict[str, int] = {}
        for w in words:
            if w not in self.stop_words and len(w) > 2 and not w.isdigit():
                freq[w] = freq.get(w, 0) + 1
        sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_kw[:top_n]]

    def extract_entities(self, text: str) -> List[str]:
        # Heuristic entity extraction: Capitalized multi-word sequences, orgs, names
        matches = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        entities = []
        for m in matches:
            if m.lower() not in self.stop_words and len(m) > 2 and m not in entities:
                entities.append(m)
        return entities[:12]

preprocessor = TextPreprocessor()
