from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Analysis, Claim, Source, User
from app.db.schemas import TextAnalysisRequest, UrlAnalysisRequest, DemoAnalysisRequest, AnalysisDetailOut
from app.ai_engine.pipeline import pipeline
from app.ai_engine.file_parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, extract_text_from_image, extract_article_from_url
from app.api.deps import get_optional_user

router = APIRouter()

def save_analysis_to_db(result: dict, user: Optional[User], db: Session) -> Analysis:
    analysis = Analysis(
        user_id=user.id if user else None,
        content_title=result.get("content_title"),
        content=result.get("content"),
        content_type=result.get("content_type", "text"),
        trust_score=result.get("trust_score", 0.0),
        classification=result.get("classification", "Unverified"),
        confidence=result.get("confidence", 0.0),
        risk_level=result.get("risk_level", "Medium"),
        explanation=result.get("explanation", ""),
        score_breakdown=result.get("score_breakdown"),
        linguistic_metrics=result.get("linguistic_metrics"),
        is_demo=result.get("is_demo", False)
    )
    db.add(analysis)
    db.flush() # get generated ID

    for claim_data in result.get("claims", []):
        claim = Claim(
            analysis_id=analysis.id,
            claim_text=claim_data.get("claim_text"),
            verdict=claim_data.get("verdict", "Unverified"),
            confidence=claim_data.get("confidence", 0.0),
            evidence=claim_data.get("evidence", ""),
            category=claim_data.get("category")
        )
        db.add(claim)

    for source_data in result.get("sources", []):
        source = Source(
            analysis_id=analysis.id,
            title=source_data.get("title", "Reference Source"),
            url=source_data.get("url"),
            credibility=source_data.get("credibility", 80.0),
            source_type=source_data.get("source_type", "reference"),
            domain=source_data.get("domain"),
            stance=source_data.get("stance")
        )
        db.add(source)

    db.commit()
    db.refresh(analysis)
    return analysis

@router.post("/text", response_model=AnalysisDetailOut)
def analyze_text(
    payload: TextAnalysisRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        result = pipeline.analyze_content(
            text=payload.text,
            title=payload.title,
            content_type="text",
            custom_weights=payload.custom_weights,
            is_demo=False
        )
        saved = save_analysis_to_db(result, current_user, db)
        return saved
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/url", response_model=AnalysisDetailOut)
def analyze_url(
    payload: UrlAnalysisRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        title, text = extract_article_from_url(payload.url)
        result = pipeline.analyze_content(
            text=text,
            title=title,
            url=payload.url,
            content_type="url",
            custom_weights=payload.custom_weights,
            is_demo=False
        )
        saved = save_analysis_to_db(result, current_user, db)
        return saved
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to analyze URL: {str(e)}")

@router.post("/file", response_model=AnalysisDetailOut)
async def analyze_file(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (maximum 10MB).")
        
    filename = file.filename.lower()
    text = ""
    
    try:
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(contents)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(contents)
        elif filename.endswith((".txt", ".md", ".csv")):
            text = extract_text_from_txt(contents)
        else:
            raise HTTPException(status_code=400, detail="Unsupported document format. Please upload PDF, DOCX, or TXT.")
            
        if not text or len(text.strip()) < 15:
            raise HTTPException(status_code=400, detail="No readable text could be extracted from document.")
            
        result = pipeline.analyze_content(
            text=text,
            title=f"Doc: {file.filename}",
            content_type="document",
            is_demo=False
        )
        saved = save_analysis_to_db(result, current_user, db)
        return saved
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process document: {str(e)}")

@router.post("/image", response_model=AnalysisDetailOut)
async def analyze_image(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image file too large (maximum 10MB).")
        
    filename = file.filename.lower()
    if not filename.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
        raise HTTPException(status_code=400, detail="Unsupported image format. Please upload PNG, JPG, or WEBP.")
        
    try:
        text = extract_text_from_image(contents, file.filename)
        result = pipeline.analyze_content(
            text=text,
            title=f"Image: {file.filename}",
            content_type="image",
            is_demo=False
        )
        saved = save_analysis_to_db(result, current_user, db)
        return saved
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image OCR: {str(e)}")

@router.post("/demo", response_model=AnalysisDetailOut)
def analyze_demo(
    payload: DemoAnalysisRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        result = pipeline.run_demo(payload.scenario)
        saved = save_analysis_to_db(result, current_user, db)
        return saved
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
