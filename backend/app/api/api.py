from fastapi import APIRouter
from app.api.endpoints import auth, analyze, history, dashboard, feedback

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["AI Analysis Engine"])
api_router.include_router(history.router, prefix="/history", tags=["Analysis History"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard & Metrics"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["User Feedback"])
