from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Auth schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Analysis Request schemas
class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000, description="Content text to analyze")
    title: Optional[str] = None
    custom_weights: Optional[Dict[str, float]] = None

class UrlAnalysisRequest(BaseModel):
    url: str = Field(..., description="URL of article or webpage to analyze")
    custom_weights: Optional[Dict[str, float]] = None

class DemoAnalysisRequest(BaseModel):
    scenario: str = Field(..., description="Preset scenario: trustworthy, misleading, false, clickbait")

# Claim and Source schemas
class ClaimBase(BaseModel):
    claim_text: str
    verdict: str # Supported, Contradicted, Unverified, Partially Supported
    confidence: float
    evidence: str
    category: Optional[str] = None

class ClaimOut(ClaimBase):
    id: int
    analysis_id: str
    
    model_config = ConfigDict(from_attributes=True)

class SourceBase(BaseModel):
    title: str
    url: Optional[str] = None
    credibility: float
    source_type: str # supporting, contradicting, reference
    domain: Optional[str] = None
    stance: Optional[str] = None

class SourceOut(SourceBase):
    id: int
    analysis_id: str
    
    model_config = ConfigDict(from_attributes=True)

# Feedback schemas
class FeedbackCreate(BaseModel):
    analysis_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class FeedbackOut(BaseModel):
    id: int
    analysis_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Detailed Analysis Output
class ScoreBreakdown(BaseModel):
    source_credibility: float
    evidence_strength: float
    claim_consistency: float
    cross_source_agreement: float
    language_manipulation_cleanliness: float
    context_completeness: float

class LinguisticMetrics(BaseModel):
    sentiment: Dict[str, Any] # positive, negative, neutral, compound
    emotional_intensity: Dict[str, float] # anger, fear, sensationalism, urgency
    clickbait_score: float # 0 to 100
    hyperbole_count: int
    readability_level: str
    word_count: int

class AnalysisSummaryOut(BaseModel):
    id: str
    user_id: Optional[int] = None
    content_title: Optional[str] = None
    content_type: str
    trust_score: float
    classification: str
    confidence: float
    risk_level: str
    is_demo: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AnalysisDetailOut(AnalysisSummaryOut):
    content: str
    explanation: str
    score_breakdown: Optional[Dict[str, float]] = None
    linguistic_metrics: Optional[Dict[str, Any]] = None
    claims: List[ClaimOut] = []
    sources: List[SourceOut] = []
    
    model_config = ConfigDict(from_attributes=True)

# Dashboard Stats Output
class DashboardStatsOut(BaseModel):
    total_analyses: int
    trustworthy_count: int
    misleading_count: int
    false_count: int
    needs_verification_count: int
    average_trust_score: float
    score_distribution: List[Dict[str, Any]]
    classification_distribution: List[Dict[str, Any]]
    recent_analyses: List[AnalysisSummaryOut]
