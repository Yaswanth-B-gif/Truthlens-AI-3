from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.api import api_router
from app.db.session import engine, Base, SessionLocal
from app.db.models import Analysis, Claim, Source
from app.ai_engine.pipeline import pipeline

# Ensure tables exist immediately
Base.metadata.create_all(bind=engine)

def seed_demo_data():
    db = SessionLocal()
    try:
        count = db.query(Analysis).count()
        if count == 0:
            scenarios = ["trustworthy", "misleading", "false", "clickbait"]
            for s in scenarios:
                res = pipeline.run_demo(s)
                analysis = Analysis(
                    content_title=res["content_title"],
                    content=res["content"],
                    content_type="demo",
                    trust_score=res["trust_score"],
                    classification=res["classification"],
                    confidence=res["confidence"],
                    risk_level=res["risk_level"],
                    explanation=res["explanation"],
                    score_breakdown=res["score_breakdown"],
                    linguistic_metrics=res["linguistic_metrics"],
                    is_demo=True
                )
                db.add(analysis)
                db.flush()
                for c in res.get("claims", []):
                    db.add(Claim(
                        analysis_id=analysis.id,
                        claim_text=c["claim_text"],
                        verdict=c["verdict"],
                        confidence=c["confidence"],
                        evidence=c["evidence"],
                        category=c.get("category")
                    ))
                for src in res.get("sources", []):
                    db.add(Source(
                        analysis_id=analysis.id,
                        title=src["title"],
                        url=src["url"],
                        credibility=src["credibility"],
                        source_type=src["source_type"],
                        domain=src.get("domain"),
                        stance=src.get("stance")
                    ))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seed info: {e}")
    finally:
        db.close()

# Pre-seed on start
seed_demo_data()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "description": settings.PROJECT_DESCRIPTION
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TruthLens AI API Gateway"}
