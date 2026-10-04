from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.db.session import get_db
from app.db.models import Analysis, User
from app.db.schemas import DashboardStatsOut, AnalysisSummaryOut
from app.api.deps import get_optional_user

router = APIRouter()

@router.get("", response_model=DashboardStatsOut)
def get_dashboard_metrics(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    q = db.query(Analysis)
    if current_user:
        q = q.filter(Analysis.user_id == current_user.id)
        
    all_records = q.all()
    total_count = len(all_records)
    
    if total_count == 0:
        return {
            "total_analyses": 0,
            "trustworthy_count": 0,
            "misleading_count": 0,
            "false_count": 0,
            "needs_verification_count": 0,
            "average_trust_score": 0.0,
            "score_distribution": [
                {"range": "0-19", "count": 0, "label": "Likely False"},
                {"range": "20-39", "count": 0, "label": "Likely Misleading"},
                {"range": "40-59", "count": 0, "label": "Needs Verification"},
                {"range": "60-79", "count": 0, "label": "Mostly Trustworthy"},
                {"range": "80-100", "count": 0, "label": "Highly Trustworthy"}
            ],
            "classification_distribution": [
                {"name": "Highly Trustworthy", "value": 0, "color": "#10B981"},
                {"name": "Mostly Trustworthy", "value": 0, "color": "#06B6D4"},
                {"name": "Needs Verification", "value": 0, "color": "#F59E0B"},
                {"name": "Likely Misleading", "value": 0, "color": "#F97316"},
                {"name": "Likely False", "value": 0, "color": "#EF4444"}
            ],
            "recent_analyses": []
        }
        
    avg_score = round(sum(a.trust_score for a in all_records) / total_count, 1)
    
    trustworthy = sum(1 for a in all_records if a.trust_score >= 60.0)
    misleading = sum(1 for a in all_records if 20.0 <= a.trust_score < 40.0)
    false_cnt = sum(1 for a in all_records if a.trust_score < 20.0)
    needs_ver = sum(1 for a in all_records if 40.0 <= a.trust_score < 60.0)
    
    # Score distribution buckets
    b_0_19 = sum(1 for a in all_records if a.trust_score < 20.0)
    b_20_39 = sum(1 for a in all_records if 20.0 <= a.trust_score < 40.0)
    b_40_59 = sum(1 for a in all_records if 40.0 <= a.trust_score < 60.0)
    b_60_79 = sum(1 for a in all_records if 60.0 <= a.trust_score < 80.0)
    b_80_100 = sum(1 for a in all_records if a.trust_score >= 80.0)
    
    score_dist = [
        {"range": "0-19", "count": b_0_19, "label": "Likely False"},
        {"range": "20-39", "count": b_20_39, "label": "Likely Misleading"},
        {"range": "40-59", "count": b_40_59, "label": "Needs Verification"},
        {"range": "60-79", "count": b_60_79, "label": "Mostly Trustworthy"},
        {"range": "80-100", "count": b_80_100, "label": "Highly Trustworthy"}
    ]
    
    class_dist = [
        {"name": "Highly Trustworthy", "value": b_80_100, "color": "#10B981"},
        {"name": "Mostly Trustworthy", "value": b_60_79, "color": "#06B6D4"},
        {"name": "Needs Verification", "value": b_40_59, "color": "#F59E0B"},
        {"name": "Likely Misleading", "value": b_20_39, "color": "#F97316"},
        {"name": "Likely False", "value": b_0_19, "color": "#EF4444"}
    ]
    
    recent = q.order_by(desc(Analysis.created_at)).limit(6).all()
    
    return {
        "total_analyses": total_count,
        "trustworthy_count": trustworthy,
        "misleading_count": misleading,
        "false_count": false_cnt,
        "needs_verification_count": needs_ver,
        "average_trust_score": avg_score,
        "score_distribution": score_dist,
        "classification_distribution": class_dist,
        "recent_analyses": recent
    }
