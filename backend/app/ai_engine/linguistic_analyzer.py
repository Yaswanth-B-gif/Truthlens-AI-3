import re
from typing import Dict, Any, List
from app.ai_engine.preprocessing import preprocessor

class LinguisticAnalyzer:
    def __init__(self):
        # Emotional lexicons
        self.fear_words = {
            "deadly", "danger", "catastrophe", "apocalypse", "collapse", "threat",
            "poison", "fatal", "lethal", "panic", "horrifying", "destructive",
            "terror", "toxic", "destroy", "epidemic", "crisis", "lethal"
        }
        self.anger_words = {
            "outrage", "furious", "betrayal", "corrupt", "treason", "scandal",
            "evil", "tyrant", "criminal", "liar", "shameful", "disgrace",
            "hate", "scam", "crooks", "fraud", "greed"
        }
        self.urgency_words = {
            "urgent", "immediately", "before it's too late", "act now", "breaking",
            "warning", "alert", "emergency", "hurry", "last chance", "right now",
            "instant", "critical"
        }
        self.sensational_words = {
            "shocking", "unbelievable", "mind-blowing", "miracle", "secret",
            "hidden", "they don't want you to know", "magic", "guaranteed",
            "stunning", "jaw-dropping", "conspiracy", "exposed", "bombshell",
            "cure-all", "proven 100%"
        }
        self.positive_sentiment = {
            "benefit", "success", "effective", "safe", "improve", "support",
            "confirmed", "solution", "reliable", "proven", "progress", "healthy",
            "advancement", "promising", "verified", "authentic"
        }
        self.negative_sentiment = {
            "harm", "failure", "risk", "damage", "corrupt", "fake", "hoax",
            "flawed", "dangerous", "deceptive", "misleading", "hazard", "threat",
            "collapse", "tragedy", "loss"
        }

    def analyze_emotional_tone(self, words: List[str]) -> Dict[str, float]:
        total_words = max(len(words), 1)
        
        fear_count = sum(1 for w in words if w in self.fear_words)
        anger_count = sum(1 for w in words if w in self.anger_words)
        urgency_count = sum(1 for w in words if w in self.urgency_words)
        sensational_count = sum(1 for w in words if w in self.sensational_words)
        
        # Scale to 0-100 percentage based on density
        fear_score = min(round((fear_count / total_words) * 600, 1), 100.0)
        anger_score = min(round((anger_count / total_words) * 600, 1), 100.0)
        urgency_score = min(round((urgency_count / total_words) * 600, 1), 100.0)
        sensational_score = min(round((sensational_count / total_words) * 600, 1), 100.0)
        
        return {
            "fear": fear_score,
            "anger": anger_score,
            "urgency": urgency_score,
            "sensationalism": sensational_score
        }

    def analyze_sentiment(self, words: List[str]) -> Dict[str, Any]:
        pos = sum(1 for w in words if w in self.positive_sentiment)
        neg = sum(1 for w in words if w in self.negative_sentiment)
        total = pos + neg
        
        if total == 0:
            return {"label": "Neutral", "positive": 0.33, "negative": 0.33, "neutral": 0.34, "compound": 0.0}
            
        pos_ratio = pos / (total + 1)
        neg_ratio = neg / (total + 1)
        compound = round((pos - neg) / (total + 2), 2)
        
        if compound >= 0.15:
            label = "Positive"
        elif compound <= -0.15:
            label = "Negative"
        else:
            label = "Neutral"
            
        return {
            "label": label,
            "positive": round(pos_ratio, 2),
            "negative": round(neg_ratio, 2),
            "neutral": round(max(0.0, 1.0 - pos_ratio - neg_ratio), 2),
            "compound": compound
        }

    def calculate_readability(self, text: str, words: List[str], sentences: List[str]) -> Dict[str, Any]:
        word_count = max(len(words), 1)
        sentence_count = max(len(sentences), 1)
        
        avg_sentence_len = round(word_count / sentence_count, 1)
        
        # Estimate syllables heuristically
        syllable_count = sum(max(1, len(re.findall(r"[aeiouy]+", w))) for w in words)
        avg_syllables_per_word = syllable_count / word_count
        
        # Flesch Reading Ease approximation = 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        flesch_score = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0.0, min(100.0, round(flesch_score, 1)))
        
        if flesch_score >= 80:
            level = "Easy / Conversational"
        elif flesch_score >= 60:
            level = "Standard / Accessible"
        elif flesch_score >= 40:
            level = "Academic / Complex"
        else:
            level = "Highly Technical / Dense"
            
        return {
            "flesch_score": flesch_score,
            "reading_level": level,
            "avg_sentence_length": avg_sentence_len,
            "word_count": word_count
        }

    def detect_clickbait(self, text: str, words: List[str]) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # Clickbait pattern matches
        clickbait_patterns = [
            r"\byou won't believe\b",
            r"\bwhat happens next\b",
            r"\bthis one trick\b",
            r"\bdoctors hate\b",
            r"\bsecret they don't want you to know\b",
            r"\bshocking truth\b",
            r"\bmiracle cure\b",
            r"\bwill blow your mind\b",
            r"\b\d+\s+reasons why\b",
            r"\bnever seen before\b"
        ]
        
        matched_patterns = [p for p in clickbait_patterns if re.search(p, text_lower)]
        
        # ALL CAPS analysis
        caps_words = re.findall(r"\b[A-Z]{3,}\b", text)
        caps_ratio = len(caps_words) / max(len(words), 1)
        
        # Exclamation mark density
        exclamations = text.count("!")
        
        score = 0.0
        score += len(matched_patterns) * 25.0
        score += min(caps_ratio * 300, 35.0)
        score += min(exclamations * 5.0, 20.0)
        
        clickbait_score = min(round(score, 1), 100.0)
        
        return {
            "clickbait_score": clickbait_score,
            "hyperbole_patterns": matched_patterns,
            "excessive_caps_count": len(caps_words),
            "exclamation_count": exclamations
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        words = preprocessor.tokenize_words(text)
        sentences = preprocessor.tokenize_sentences(text)
        
        emotional = self.analyze_emotional_tone(words)
        sentiment = self.analyze_sentiment(words)
        readability = self.calculate_readability(text, words, sentences)
        clickbait = self.detect_clickbait(text, words)
        
        # Manipulation penalty: Higher emotional intensity + clickbait lowers cleanliness score
        manipulation_penalty = (
            (emotional["sensationalism"] * 0.35) +
            (emotional["fear"] * 0.25) +
            (emotional["anger"] * 0.20) +
            (clickbait["clickbait_score"] * 0.20)
        )
        cleanliness_score = max(0.0, min(100.0, round(100.0 - manipulation_penalty, 1)))
        
        return {
            "sentiment": sentiment,
            "emotional_intensity": emotional,
            "clickbait_score": clickbait["clickbait_score"],
            "hyperbole_count": len(clickbait["hyperbole_patterns"]) + clickbait["excessive_caps_count"],
            "readability_level": readability["reading_level"],
            "flesch_score": readability["flesch_score"],
            "word_count": readability["word_count"],
            "manipulation_cleanliness_score": cleanliness_score
        }

linguistic_analyzer = LinguisticAnalyzer()
