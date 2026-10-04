import re
from typing import Dict, Any, Optional, List
from app.ai_engine.preprocessing import preprocessor
from app.ai_engine.claim_extractor import claim_extractor
from app.ai_engine.linguistic_analyzer import linguistic_analyzer
from app.ai_engine.credibility_analyzer import credibility_analyzer
from app.ai_engine.evidence_retriever import evidence_retriever
from app.ai_engine.trust_scorer import trust_scorer

DEMO_SCENARIOS = {
    "trustworthy": {
        "title": "NASA James Webb Telescope Confirms Oldest Known Galaxies Formed Near Cosmic Dawn",
        "text": """Astronomers utilizing the James Webb Space Telescope (JWST) have confirmed the discovery of several galaxies dating back to just 330 million years after the Big Bang. According to peer-reviewed findings published in Nature Astronomy, spectroscopic analysis reveals distinct chemical signatures in the JADES-GS-z14-0 galaxy.

Lead researchers from NASA, the European Space Agency (ESA), and Cambridge University corroborated that these ancient stellar clusters formed rapidly with high luminosity. The data confirms previous cosmological models regarding early stellar formation while opening new avenues for understanding primordial cosmic reionization. Multiple international observatories, including the Hubble Space Telescope and the Atacama Large Millimeter Array (ALMA), provided independent cross-calibration.""",
        "url": "https://www.nasa.gov/mission_pages/webb/science/early-universe"
    },
    "misleading": {
        "title": "Daily Wellness Digest: Drinking Hot Alkaline Lemon Water Cures 98% of Illnesses",
        "text": """Drinking a cup of boiling alkaline water with fresh lemon slices every morning is guaranteed to kill cancer cells and destroy all toxic acidity in your body. Leading alternative health practitioners claim that pharmaceutical companies are hiding this ancient miracle secret because it costs virtually nothing.

According to Dr. Marcus Vance, a holistic lifestyle coach, cancer cannot survive in an alkaline environment. Studies supposedly show a 98% reduction in chronic fatigue and immune disorders within just 7 days of daily lemon water consumption. While conventional doctors dismiss these claims, millions of people worldwide report miraculous recoveries without any medical intervention.""",
        "url": "https://wellness-daily-secrets.xyz/cure-all"
    },
    "false": {
        "title": "EMERGENCY LEAK: Secret 5G Tower Signals Activate Inoculation Nanobots",
        "text": """BREAKING EXPOSE! Secret government whistleblower documents leak that new 5G cellular communication towers are transmitting low-frequency microwave frequencies to activate magnetic microchips hidden inside global vaccines. 

Insiders confirm the military has enacted covert martial law directives to track citizen movements through synthetic electromagnetic bio-circuits. DO NOT allow mainstream media to suppress this truth! The global financial system will be collapsed overnight to enforce full digital slavery unless citizens disconnect immediately! SHARE THIS EVERYWHERE BEFORE IT GETS DELETED!""",
        "url": "https://shadow-truth-leaks.top/emergency-expose"
    },
    "clickbait": {
        "title": "SHOCKING! You Won't Believe What Doctors Found Inside This Everyday Kitchen Fruit!",
        "text": """Doctors are FURIOUS! This ONE simple kitchen trick is blowing minds across the internet and big pharma is panicking! You won't believe what happens when you consume this overlooked exotic fruit before bedtime!

Experts were left completely SPEECHLESS after discovering that eating just two bites burns 40 pounds of stubborn belly fat in 48 hours without exercise or dieting. Millions are rushing to buy it before supplies are banned forever! Click to see the jaw-dropping proof that will leave you stunned!""",
        "url": "https://viral-buzz-today.click/shocking-belly-fat-secret"
    }
}

class AIAnalysisPipeline:
    def analyze_content(
        self,
        text: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        content_type: str = "text",
        custom_weights: Optional[Dict[str, float]] = None,
        is_demo: bool = False
    ) -> Dict[str, Any]:
        # 1. Content Preprocessing
        cleaned_text = preprocessor.clean_text(text)
        if not cleaned_text or len(cleaned_text) < 15:
            raise ValueError("Input content is too short or empty for AI fact analysis.")
            
        if not title:
            sentences = preprocessor.tokenize_sentences(cleaned_text)
            title = sentences[0][:80] + "..." if len(sentences[0]) > 80 else sentences[0]

        # 2. Linguistic & Tone Analysis
        linguistic = linguistic_analyzer.analyze(cleaned_text)
        
        # 3. Claim Extraction & Decomposition
        extracted_claims = claim_extractor.extract_claims(cleaned_text)
        
        # 4. Source & Credibility Assessment
        credibility = credibility_analyzer.evaluate_source(url=url, text=cleaned_text)
        
        # 5. Evidence Retrieval & Cross-Verification
        verified_claims, sources, cross_agreement_score = evidence_retriever.verify_claims(extracted_claims)
        
        # 6. Calculate Component Scores
        # Claim consistency: Ratio of supported vs contradicted claims
        supported_c = sum(1 for c in verified_claims if c["verdict"] == "Supported")
        contradicted_c = sum(1 for c in verified_claims if c["verdict"] == "Contradicted")
        total_c = max(len(verified_claims), 1)
        
        claim_consistency_score = round(max(5.0, min(100.0, (
            (supported_c * 100.0) + 
            ((total_c - supported_c - contradicted_c) * 50.0)
        ) / total_c)), 1)
        
        # Evidence strength score based on source credibility and citations
        evidence_strength_score = round(max(10.0, min(100.0, (
            (credibility["source_credibility_score"] * 0.6) +
            (cross_agreement_score * 0.4)
        ))), 1)
        
        # Context completeness: based on word count, citations, and claim count
        context_score = min(100.0, max(20.0, (
            min(linguistic["word_count"] / 4.0, 50.0) +
            (credibility["citations_detected"] * 10.0) +
            (len(extracted_claims) * 5.0)
        )))
        
        # 7. Final Weighted Trust Score Computation
        score_result = trust_scorer.compute_trust_score(
            source_score=credibility["source_credibility_score"],
            evidence_score=evidence_strength_score,
            claim_consistency_score=claim_consistency_score,
            cross_agreement_score=cross_agreement_score,
            cleanliness_score=linguistic["manipulation_cleanliness_score"],
            context_score=context_score,
            custom_weights=custom_weights
        )
        
        # 8. Generate XAI Rationale
        explanation = trust_scorer.generate_explanation(
            trust_score=score_result["trust_score"],
            classification=score_result["classification"],
            confidence=score_result["confidence"],
            claims=verified_claims,
            linguistic=linguistic,
            credibility=credibility
        )
        
        return {
            "content_title": title,
            "content": cleaned_text,
            "content_type": content_type,
            "trust_score": score_result["trust_score"],
            "classification": score_result["classification"],
            "confidence": score_result["confidence"],
            "risk_level": score_result["risk_level"],
            "explanation": explanation,
            "score_breakdown": score_result["score_breakdown"],
            "linguistic_metrics": linguistic,
            "claims": verified_claims,
            "sources": sources,
            "is_demo": is_demo
        }

    def run_demo(self, scenario_key: str = "trustworthy") -> Dict[str, Any]:
        scenario = DEMO_SCENARIOS.get(scenario_key.lower(), DEMO_SCENARIOS["trustworthy"])
        return self.analyze_content(
            text=scenario["text"],
            title=scenario["title"],
            url=scenario["url"],
            content_type="demo",
            is_demo=True
        )

pipeline = AIAnalysisPipeline()
