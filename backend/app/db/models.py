import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user")

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    content_title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False, default="text") # text, url, document, image, demo
    trust_score = Column(Float, nullable=False) # 0 to 100
    classification = Column(String(100), nullable=False) # Highly Trustworthy, Mostly Trustworthy, Needs Verification, Likely Misleading, Likely False
    confidence = Column(Float, nullable=False) # 0 to 100
    risk_level = Column(String(50), nullable=False) # Low, Medium, High, Critical
    explanation = Column(Text, nullable=False)
    score_breakdown = Column(JSON, nullable=True) # dictionary of breakdown scores
    linguistic_metrics = Column(JSON, nullable=True) # sentiment, emotional tone, clickbait, readability
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    user = relationship("User", back_populates="analyses")
    claims = relationship("Claim", back_populates="analysis", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="analysis", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="analysis", cascade="all, delete-orphan")

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    verdict = Column(String(50), nullable=False) # Supported, Contradicted, Unverified, Partially Supported
    confidence = Column(Float, nullable=False) # 0 to 100
    evidence = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    
    analysis = relationship("Analysis", back_populates="claims")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    credibility = Column(Float, nullable=False) # 0 to 100
    source_type = Column(String(50), nullable=False) # supporting, contradicting, reference
    domain = Column(String(255), nullable=True)
    stance = Column(String(50), nullable=True)
    
    analysis = relationship("Analysis", back_populates="sources")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, nullable=False) # 1 to 5 or 1 (thumbs up) / 0 (thumbs down)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    analysis = relationship("Analysis", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")
