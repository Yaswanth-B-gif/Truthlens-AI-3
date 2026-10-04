import re
from typing import List, Dict, Any
from app.ai_engine.preprocessing import preprocessor

class ClaimExtractor:
    def __init__(self):
        # Patterns that strongly signal factual claims or assertions
        self.claim_indicators = [
            r"\b(proven|confirmed|revealed|discovered|stated|reported|claims|found that|demonstrates|shows that)\b",
            r"\b(causes|leads to|results in|prevents|cures|destroys|increases|decreases|linked to)\b",
            r"\b(\d+%\s+|\$\d+|\b\d+\s+billion|\b\d+\s+million|\b\d+\s+percent|\b\d{4}\b)\b",
            r"\b(according to|study by|researchers from|official|government|scientists|dr\.|expert)\b",
            r"\b(secretly|conspiracy|hoax|miracle|guaranteed|hidden truth|leak)\b"
        ]
        
    def is_potential_claim(self, sentence: str) -> bool:
        # Ignore short strings, questions, imperatives
        if len(sentence.split()) < 5:
            return False
        if sentence.endswith("?") and not any(ind in sentence.lower() for ind in ["secret", "hoax", "cure"]):
            return False
            
        sentence_lower = sentence.lower()
        for pattern in self.claim_indicators:
            if re.search(pattern, sentence_lower):
                return True
                
        # Substantial declarative sentence with subject and predicate
        words = sentence.split()
        if len(words) >= 8 and not sentence.strip().startswith(("How", "Why", "What", "When", "Where", "Who?")):
            return True
            
        return False

    def categorize_claim(self, claim_text: str) -> str:
        text_lower = claim_text.lower()
        if re.search(r"\b(\d+%\s+|\$\d+|\b\d+\s+billion|\b\d+\s+percent|\b\d+\b)", text_lower):
            return "Statistical / Quantitative"
        elif re.search(r"\b(causes|leads to|results in|cures|prevents|triggers)\b", text_lower):
            return "Causal / Health / Scientific"
        elif re.search(r"\b(according to|study|researchers|university|dr\.|spokesperson|officials)\b", text_lower):
            return "Attribution / Authority"
        elif re.search(r"\b(government|election|minister|president|law|court|policy)\b", text_lower):
            return "Political / Policy"
        else:
            return "General Factual Assertion"

    def extract_claims(self, text: str, max_claims: int = 6) -> List[Dict[str, Any]]:
        sentences = preprocessor.tokenize_sentences(text)
        candidates = []
        
        for idx, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if self.is_potential_claim(sentence):
                category = self.categorize_claim(sentence)
                candidates.append({
                    "id": idx + 1,
                    "claim_text": sentence,
                    "category": category
                })
                
        # If no claim was matched by heuristic rules, use top sentences
        if not candidates and sentences:
            for idx, s in enumerate(sentences[:3]):
                candidates.append({
                    "id": idx + 1,
                    "claim_text": s,
                    "category": self.categorize_claim(s)
                })
                
        return candidates[:max_claims]

claim_extractor = ClaimExtractor()
