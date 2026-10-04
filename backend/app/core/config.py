import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TruthLens AI"
    PROJECT_DESCRIPTION: str = "Data-Driven Detection of False Information and Trustworthy Content on Digital Platforms"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = "truthlens-ai-secure-random-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./truthlens.db"
    
    # AI / External API keys
    AI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Configurable Scoring Weights (Must sum to 1.0)
    WEIGHT_SOURCE_CREDIBILITY: float = 0.25
    WEIGHT_EVIDENCE_STRENGTH: float = 0.25
    WEIGHT_CLAIM_CONSISTENCY: float = 0.20
    WEIGHT_CROSS_SOURCE_AGREEMENT: float = 0.15
    WEIGHT_LANGUAGE_MANIPULATION: float = 0.10
    WEIGHT_CONTEXT_COMPLETENESS: float = 0.05
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
