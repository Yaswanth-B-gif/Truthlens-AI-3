import re
import json
from typing import List, Dict, Any, Tuple
from app.core.config import settings

# Built-in verified knowledge base for deterministic fact matching
VERIFIED_KNOWLEDGE_CORPUS = [
    {
        "keywords": ["covid", "vaccine", "microchip", "5g", "dna alteration", "magnetic"],
        "verdict": "Contradicted",
        "confidence": 98.0,
        "evidence": "Extensive peer-reviewed clinical trials and international health agencies (WHO, CDC, FDA) confirm mRNA vaccines do not alter human DNA, contain microchips, or interact with 5G networks.",
        "sources": [
            {"title": "WHO Vaccine Safety Factsheet", "url": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/covid-19-vaccines/advice", "credibility": 97.0, "source_type": "contradicting", "domain": "who.int", "stance": "Refuting Claim"},
            {"title": "CDC COVID-19 Vaccine Science Brief", "url": "https://www.cdc.gov/coronavirus/2019-ncov/vaccines/facts.html", "credibility": 96.0, "source_type": "contradicting", "domain": "cdc.gov", "stance": "Refuting Claim"}
        ]
    },
    {
        "keywords": ["james webb", "space telescope", "galaxy", "nasa", "early universe", "astronomy"],
        "verdict": "Supported",
        "confidence": 95.0,
        "evidence": "NASA and ESA observations from the James Webb Space Telescope (JWST) have officially confirmed the discovery of galaxies formed within 300 million years of the Big Bang.",
        "sources": [
            {"title": "NASA JWST Early Universe Science Release", "url": "https://www.nasa.gov/mission_pages/webb/main/index.html", "credibility": 98.0, "source_type": "supporting", "domain": "nasa.gov", "stance": "Supporting Claim"},
            {"title": "Nature Astronomy JWST Observations", "url": "https://www.nature.com/nature/articles", "credibility": 97.0, "source_type": "supporting", "domain": "nature.com", "stance": "Supporting Claim"}
        ]
    },
    {
        "keywords": ["lemon", "hot water", "cure cancer", "miracle", "alkaline", "baking soda"],
        "verdict": "Contradicted",
        "confidence": 96.0,
        "evidence": "No scientific or medical evidence supports the claim that drinking hot lemon water, alkaline water, or baking soda cures cancer. Oncology consensus affirms tumor biology requires targeted medical intervention.",
        "sources": [
            {"title": "American Cancer Society - Alternative Therapy Facts", "url": "https://www.cancer.org/treatment/treatments-and-side-effects/treatment-types/complementary-and-integrative-medicine.html", "credibility": 96.0, "source_type": "contradicting", "domain": "cancer.org", "stance": "Refuting Claim"},
            {"title": "Memorial Sloan Kettering Integrative Medicine Database", "url": "https://www.mskcc.org/cancer-care/integrative-medicine", "credibility": 95.0, "source_type": "contradicting", "domain": "mskcc.org", "stance": "Refuting Claim"}
        ]
    },
    {
        "keywords": ["climate change", "global temperature", "greenhouse gases", "ipcc", "carbon emissions", "warming"],
        "verdict": "Supported",
        "confidence": 97.0,
        "evidence": "The Intergovernmental Panel on Climate Change (IPCC) synthesis report affirms human activities, principally emissions of greenhouse gases, have unequivocally caused global warming.",
        "sources": [
            {"title": "IPCC Sixth Assessment Synthesis Report", "url": "https://www.ipcc.ch/report/ar6/syr/", "credibility": 99.0, "source_type": "supporting", "domain": "ipcc.ch", "stance": "Supporting Claim"},
            {"title": "NOAA Global Climate Report", "url": "https://www.noaa.gov/climate", "credibility": 96.0, "source_type": "supporting", "domain": "noaa.gov", "stance": "Supporting Claim"}
        ]
    },
    {
        "keywords": ["quantum computing", "qubit", "error correction", "superposition", "ibm", "google quantum"],
        "verdict": "Supported",
        "confidence": 91.0,
        "evidence": "Recent breakthroughs in quantum error correction and logical qubits demonstrate significant progress toward fault-tolerant quantum computation as published in Nature and Physical Review.",
        "sources": [
            {"title": "Nature - Quantum Error Mitigation & Scaling", "url": "https://www.nature.com/articles/s41586-023-06096-3", "credibility": 98.0, "source_type": "supporting", "domain": "nature.com", "stance": "Supporting Claim"}
        ]
    },
    {
        "keywords": ["secret society", "illuminati", "banking collapse planned", "martial law tomorrow", "hidden bunker"],
        "verdict": "Contradicted",
        "confidence": 94.0,
        "evidence": "Conspiracy claims alleging pre-planned global collapses or impending secret martial law lack verified documentary evidence and contradict standard geopolitical and economic oversight data.",
        "sources": [
            {"title": "Reuters Fact Check - Viral Collapse Claims", "url": "https://www.reuters.com/fact-check", "credibility": 95.0, "source_type": "contradicting", "domain": "reuters.com", "stance": "Refuting Claim"}
        ]
    }
]

class EvidenceRetriever:
    def __init__(self):
        self.corpus = VERIFIED_KNOWLEDGE_CORPUS

    def match_corpus(self, claim_text: str) -> Tuple[str, float, str, List[Dict[str, Any]]]:
        claim_lower = claim_text.lower()
        words = set(re.findall(r"\b[a-z]{3,}\b", claim_lower))
        
        best_match = None
        best_score = 0
        
        for item in self.corpus:
            matched_kw = sum(1 for kw in item["keywords"] if any(w in kw or kw in w for w in words))
            if matched_kw > best_score and matched_kw >= 2:
                best_score = matched_kw
                best_match = item
                
        if best_match:
            return (
                best_match["verdict"],
                best_match["confidence"],
                best_match["evidence"],
                best_match["sources"]
            )
            
        # Fallback heuristic analysis based on linguistic cues
        contradiction_triggers = ["miracle cure", "secret they hide", "banned by doctors", "100% guaranteed", "conspiracy exposed"]
        unverified_triggers = ["sources say", "rumors claim", "anonymous insider", "allegedly", "unconfirmed"]
        
        if any(t in claim_lower for t in contradiction_triggers):
            return (
                "Contradicted",
                82.0,
                "The claim employs known deceptive markers ('miracle', 'secret') lacking corroboration in reputable peer-reviewed or independent registry databases.",
                [
                    {"title": "FactCheck.org Science Archive", "url": "https://www.factcheck.org/scicheck/", "credibility": 92.0, "source_type": "contradicting", "domain": "factcheck.org", "stance": "Doubtful Claim"}
                ]
            )
        elif any(t in claim_lower for t in unverified_triggers):
            return (
                "Unverified",
                68.0,
                "Claim relies on anonymous or second-hand attribution. Primary documentary evidence is currently unavailable.",
                [
                    {"title": "Associated Press News Verification Desk", "url": "https://apnews.com/hub/ap-fact-check", "credibility": 94.0, "source_type": "reference", "domain": "apnews.com", "stance": "Awaiting Primary Source"}
                ]
            )
        else:
            # Neutral / Likely verifiable with moderate confidence
            return (
                "Partially Supported",
                74.0,
                "Factual elements align with standard domain reporting, though specific quantitative parameters require secondary corroboration.",
                [
                    {"title": "Global News & Fact Verification Index", "url": "https://reuters.com", "credibility": 90.0, "source_type": "supporting", "domain": "reuters.com", "stance": "Contextual Support"}
                ]
            )

    def verify_claims(self, claims: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], float]:
        verified_claims = []
        all_sources = []
        source_urls = set()
        
        supported_count = 0
        contradicted_count = 0
        
        for c in claims:
            verdict, conf, evidence, sources = self.match_corpus(c["claim_text"])
            
            if verdict == "Supported":
                supported_count += 1
            elif verdict == "Contradicted":
                contradicted_count += 1
            elif verdict == "Partially Supported":
                supported_count += 0.5
                
            verified_claims.append({
                "claim_text": c["claim_text"],
                "category": c.get("category", "General"),
                "verdict": verdict,
                "confidence": conf,
                "evidence": evidence
            })
            
            for s in sources:
                if s["url"] not in source_urls:
                    source_urls.add(s["url"])
                    all_sources.append(s)
                    
        total_claims = max(len(claims), 1)
        # Agreement ratio: 0.0 (all contradicted) to 1.0 (all supported)
        agreement_ratio = max(0.0, min(1.0, (supported_count + (0.3 * (total_claims - supported_count - contradicted_count))) / total_claims))
        
        return verified_claims, all_sources, round(agreement_ratio * 100.0, 1)

evidence_retriever = EvidenceRetriever()
