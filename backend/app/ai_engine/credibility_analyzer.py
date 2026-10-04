import re
from urllib.parse import urlparse
from typing import Dict, Any, List

class CredibilityAnalyzer:
    def __init__(self):
        # Recognized high-credibility domains & institutions
        self.high_credibility_domains = {
            "reuters.com": 96.0, "apnews.com": 96.0, "bbc.com": 94.0, "bbc.co.uk": 94.0,
            "nature.com": 98.0, "science.org": 98.0, "nih.gov": 97.0, "cdc.gov": 96.0,
            "who.int": 96.0, "nejm.org": 98.0, "thelancet.com": 98.0, "nasa.gov": 97.0,
            "nytimes.com": 90.0, "washingtonpost.com": 89.0, "theguardian.com": 89.0,
            "wsj.com": 91.0, "economist.com": 92.0, "scientificamerican.com": 94.0,
            "snopes.com": 93.0, "factcheck.org": 94.0, "politifact.com": 93.0,
            "ieee.org": 96.0, "acm.org": 96.0, "arxiv.org": 92.0, "mit.edu": 95.0,
            "stanford.edu": 95.0, "harvard.edu": 95.0, "ox.ac.uk": 95.0, "cam.ac.uk": 95.0
        }
        
        # Recognized low-credibility, satirical, or sensational domains
        self.low_credibility_domains = {
            "theonion.com": 15.0, "babylonbee.com": 15.0, "infowars.com": 10.0,
            "naturalnews.com": 12.0, "worldnewsdailyreport.com": 5.0, "beforeitsnews.com": 10.0,
            "newswars.com": 12.0, "yournewswire.com": 8.0, "empirenews.net": 10.0
        }
        
        self.reputable_tlds = {".gov": 95.0, ".edu": 93.0, ".org": 82.0, ".ac.uk": 94.0}
        self.suspicious_tlds = {".xyz": 45.0, ".top": 40.0, ".click": 35.0, ".buzz": 40.0, ".info": 50.0}

    def extract_domain(self, url: str) -> str:
        if not url:
            return ""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return ""

    def evaluate_source(self, url: str = None, text: str = "") -> Dict[str, Any]:
        score = 65.0 # baseline neutral score
        domain = self.extract_domain(url) if url else ""
        citations_found = []
        
        # Check domain reputation
        if domain:
            if domain in self.high_credibility_domains:
                score = self.high_credibility_domains[domain]
            elif domain in self.low_credibility_domains:
                score = self.low_credibility_domains[domain]
            else:
                for tld, tld_score in self.reputable_tlds.items():
                    if domain.endswith(tld):
                        score = max(score, tld_score)
                        break
                for s_tld, s_score in self.suspicious_tlds.items():
                    if domain.endswith(s_tld):
                        score = min(score, s_score)
                        break
        
        # Check for inline citations / links / references in text
        url_matches = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", text)
        doi_matches = re.findall(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b", text)
        academic_cites = re.findall(r"\b(?:et al\.|journal of|proceedings of|published in|doi:)\b", text, re.IGNORECASE)
        
        citations_count = len(url_matches) + (len(doi_matches) * 2) + len(academic_cites)
        
        # Boost or adjust score based on citations
        if citations_count >= 3:
            score = min(100.0, score + 15.0)
            citations_found.append(f"Found {citations_count} structured references/citations")
        elif citations_count >= 1:
            score = min(100.0, score + 8.0)
            citations_found.append(f"Found {citations_count} external reference(s)")
            
        # Check for author attribution signals
        author_patterns = [
            r"\bby\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
            r"\bauthor:\s*([^\n\r]+)",
            r"\breported by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b"
        ]
        has_author = any(re.search(p, text, re.IGNORECASE) for p in author_patterns)
        if has_author:
            score = min(100.0, score + 5.0)
            
        return {
            "source_credibility_score": round(max(5.0, min(100.0, score)), 1),
            "domain": domain if domain else "Unspecified / Direct Text Input",
            "has_author_attribution": has_author,
            "citations_detected": citations_count,
            "citations_details": citations_found
        }

credibility_analyzer = CredibilityAnalyzer()
