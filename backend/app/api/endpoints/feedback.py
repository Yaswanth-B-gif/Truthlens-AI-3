from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Feedback, Analysis, User
from app.db.schemas import FeedbackCreate, FeedbackOut
from app.api.deps import get_optional_user

router = APIRouter()

@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == payload.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")
        
    feedback = Feedback(
        analysis_id=payload.analysis_id,
        user_id=current_user.id if current_user else None,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
