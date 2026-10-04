from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.db.models import Analysis, User
from app.db.schemas import AnalysisSummaryOut, AnalysisDetailOut
from app.api.deps import get_optional_user

router = APIRouter()

@router.get("", response_model=List[AnalysisSummaryOut])
def get_history(
    classification: Optional[str] = None,
    content_type: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    q = db.query(Analysis)
    
    if current_user:
        q = q.filter(Analysis.user_id == current_user.id)
        
    if classification and classification.lower() != "all":
        q = q.filter(Analysis.classification.ilike(f"%{classification}%"))
        
    if content_type and content_type.lower() != "all":
        q = q.filter(Analysis.content_type == content_type.lower())
        
    if query:
        q = q.filter((Analysis.content.ilike(f"%{query}%")) | (Analysis.content_title.ilike(f"%{query}%")))
        
    results = q.order_by(desc(Analysis.created_at)).limit(limit).all()
    return results

@router.get("/{analysis_id}", response_model=AnalysisDetailOut)
def get_analysis_by_id(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")
    return analysis

@router.delete("/{analysis_id}", status_code=status.HTTP_200_OK)
def delete_analysis(
    analysis_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")
        
    if current_user and analysis.user_id and analysis.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this record.")
        
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted successfully", "id": analysis_id}

@router.delete("/clear/all", status_code=status.HTTP_200_OK)
def clear_all_history(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    if current_user:
        db.query(Analysis).filter(Analysis.user_id == current_user.id).delete()
    else:
        db.query(Analysis).filter(Analysis.user_id.is_(None)).delete()
    db.commit()
    return {"message": "History cleared successfully"}
