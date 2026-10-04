from typing import Dict, Any, List, Optional
from app.core.config import settings

class TrustScorer:
    def __init__(self):
        self.default_weights = {
            "source_credibility": settings.WEIGHT_SOURCE_CREDIBILITY,
            "evidence_strength": settings.WEIGHT_EVIDENCE_STRENGTH,
            "claim_consistency": settings.WEIGHT_CLAIM_CONSISTENCY,
            "cross_source_agreement": settings.WEIGHT_CROSS_SOURCE_AGREEMENT,
            "language_manipulation_cleanliness": settings.WEIGHT_LANGUAGE_MANIPULATION,
            "context_completeness": settings.WEIGHT_CONTEXT_COMPLETENESS
        }

    def compute_trust_score(
        self,
        source_score: float,
        evidence_score: float,
        claim_consistency_score: float,
        cross_agreement_score: float,
        cleanliness_score: float,
        context_score: float,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        weights = dict(self.default_weights)
        if custom_weights:
            # Normalize custom weights so they sum to 1.0
            total_custom = sum(custom_weights.values())
            if total_custom > 0:
                weights.update({k: v / total_custom for k, v in custom_weights.items()})

        # Weighted calculation
        final_score = (
            (source_score * weights["source_credibility"]) +
            (evidence_score * weights["evidence_strength"]) +
            (claim_consistency_score * weights["claim_consistency"]) +
            (cross_agreement_score * weights["cross_source_agreement"]) +
            (cleanliness_score * weights["language_manipulation_cleanliness"]) +
            (context_score * weights["context_completeness"])
        )
        
        final_score = round(max(0.0, min(100.0, final_score)), 1)
        
        # Classification Mapping
        if final_score >= 80.0:
            classification = "Highly Trustworthy"
            risk_level = "Low"
            base_confidence = 92.0
        elif final_score >= 60.0:
            classification = "Mostly Trustworthy"
            risk_level = "Moderate"
            base_confidence = 85.0
        elif final_score >= 40.0:
            classification = "Needs Verification"
            risk_level = "Elevated"
            base_confidence = 78.0
        elif final_score >= 20.0:
            classification = "Likely Misleading"
            risk_level = "High"
            base_confidence = 88.0
        else:
            classification = "Likely False"
            risk_level = "Critical"
            base_confidence = 94.0

        # Adjust confidence by evidence and agreement
        confidence = round(min(99.0, max(60.0, (base_confidence * 0.6) + (evidence_score * 0.2) + (cleanliness_score * 0.2))), 1)

        breakdown = {
            "source_credibility": round(source_score, 1),
            "evidence_strength": round(evidence_score, 1),
            "claim_consistency": round(claim_consistency_score, 1),
            "cross_source_agreement": round(cross_agreement_score, 1),
            "language_manipulation_cleanliness": round(cleanliness_score, 1),
            "context_completeness": round(context_score, 1)
        }

        return {
            "trust_score": final_score,
            "classification": classification,
            "confidence": confidence,
            "risk_level": risk_level,
            "score_breakdown": breakdown,
            "weights_applied": weights
        }

    def generate_explanation(
        self,
        trust_score: float,
        classification: str,
        confidence: float,
        claims: List[Dict[str, Any]],
        linguistic: Dict[str, Any],
        credibility: Dict[str, Any]
    ) -> str:
        supported_claims = sum(1 for c in claims if c.get("verdict") == "Supported")
        contradicted_claims = sum(1 for c in claims if c.get("verdict") == "Contradicted")
        total_claims = len(claims)
        
        clickbait_score = linguistic.get("clickbait_score", 0)
        emotional = linguistic.get("emotional_intensity", {})
        high_emotion = any(v > 40.0 for v in emotional.values())
        
        lines = []
        
        if classification in ["Highly Trustworthy", "Mostly Trustworthy"]:
            lines.append(f"The content received an overall Trust Score of {trust_score}/100 ({classification}) with {confidence}% confidence.")
            lines.append(f"Key factual claims ({supported_claims} of {total_claims} verified) align with established scientific consensus and authoritative journalistic standards.")
            if credibility.get("citations_detected", 0) > 0:
                lines.append(f"The source includes explicit external citations and avoids sensationalized rhetoric (cleanliness rating: {linguistic.get('manipulation_cleanliness_score')}/100).")
            else:
                lines.append("Language structure remains objective with minimal emotional manipulation signals.")
        elif classification == "Needs Verification":
            lines.append(f"The content received an ambiguous Trust Score of {trust_score}/100 ({classification}) with {confidence}% confidence.")
            lines.append(f"While certain assertions appear plausible, {total_claims - supported_claims} claim(s) lack definitive primary evidence or rely on secondary hearsay.")
            lines.append("Readers are strongly advised to cross-examine independent primary registries before relying on these statements.")
        else: # Likely Misleading or Likely False
            lines.append(f"The content received a critical Trust Score of {trust_score}/100 ({classification}) with {confidence}% confidence.")
            if contradicted_claims > 0:
                lines.append(f"Direct contradiction was identified in {contradicted_claims} core assertion(s) against verified scientific and factual registries.")
            if clickbait_score > 30 or high_emotion:
                lines.append(f"The analysis detected strong linguistic manipulation indicators (clickbait score: {clickbait_score}/100, elevated urgency/sensationalism markers).")
            lines.append("The absence of credible empirical sources and presence of exaggerated claims strongly indicate disinformation or deceptive intent.")

        return " ".join(lines)

trust_scorer = TrustScorer()
