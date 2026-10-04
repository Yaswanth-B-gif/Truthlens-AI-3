import pytest
from app.ai_engine.preprocessing import preprocessor
from app.ai_engine.claim_extractor import claim_extractor
from app.ai_engine.linguistic_analyzer import linguistic_analyzer
from app.ai_engine.credibility_analyzer import credibility_analyzer
from app.ai_engine.trust_scorer import trust_scorer
from app.ai_engine.pipeline import pipeline

def test_text_preprocessing():
    raw = "  Scientists at NASA have confirmed water on the Moon!   Multiple studies agree.  "
    cleaned = preprocessor.clean_text(raw)
    assert "Scientists at NASA" in cleaned
    sentences = preprocessor.tokenize_sentences(cleaned)
    assert len(sentences) >= 2
    keywords = preprocessor.extract_keywords(cleaned)
    assert "scientists" in keywords or "nasa" in keywords or "moon" in keywords

def test_claim_extraction():
    sample = "According to researchers from MIT, drinking green tea reduces cardiovascular risk by 25%. Also, the president signed a new environmental bill today."
    claims = claim_extractor.extract_claims(sample)
    assert len(claims) >= 1
    assert any("green tea" in c["claim_text"].lower() or "cardiovascular" in c["claim_text"].lower() for c in claims)

def test_linguistic_analysis():
    neutral_text = "The quarterly economic report indicates moderate inflation of 2.1% across major industrial sectors."
    clickbait_text = "SHOCKING! You won't believe the secret miracle cure that big pharma is hiding right now! Act now before it's too late!"
    
    res_neutral = linguistic_analyzer.analyze(neutral_text)
    res_clickbait = linguistic_analyzer.analyze(clickbait_text)
    
    assert res_clickbait["clickbait_score"] > res_neutral["clickbait_score"]
    assert res_neutral["manipulation_cleanliness_score"] > res_clickbait["manipulation_cleanliness_score"]

def test_credibility_analyzer():
    source_reputable = credibility_analyzer.evaluate_source(url="https://www.nature.com/articles/sample", text="Published in nature doi:10.1038/s41586-023")
    source_suspicious = credibility_analyzer.evaluate_source(url="https://secret-news-exposed.click/scandal", text="No authors mentioned anywhere.")
    
    assert source_reputable["source_credibility_score"] > source_suspicious["source_credibility_score"]

def test_trust_scorer():
    high_score = trust_scorer.compute_trust_score(
        source_score=95.0,
        evidence_score=90.0,
        claim_consistency_score=95.0,
        cross_agreement_score=90.0,
        cleanliness_score=95.0,
        context_score=85.0
    )
    assert high_score["trust_score"] >= 80.0
    assert high_score["classification"] == "Highly Trustworthy"
    assert high_score["risk_level"] == "Low"
    
    low_score = trust_scorer.compute_trust_score(
        source_score=15.0,
        evidence_score=10.0,
        claim_consistency_score=10.0,
        cross_agreement_score=10.0,
        cleanliness_score=20.0,
        context_score=30.0
    )
    assert low_score["trust_score"] < 40.0
    assert low_score["risk_level"] in ["High", "Critical"]

def test_pipeline_demo_scenarios():
    trustworthy = pipeline.run_demo("trustworthy")
    assert trustworthy["trust_score"] >= 70.0
    assert trustworthy["classification"] in ["Highly Trustworthy", "Mostly Trustworthy"]
    assert len(trustworthy["claims"]) > 0
    assert len(trustworthy["sources"]) > 0

    false_demo = pipeline.run_demo("false")
    assert false_demo["trust_score"] < 50.0
    assert false_demo["risk_level"] in ["Elevated", "High", "Critical"]
