from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.resume import Resume
from models.resume_analysis import ResumeAnalysis
from models.user import User
from schemas.resume_analysis import ResumeAnalysisResponse
from services.azure_blob_download import download_blob
from services.pdf_extractor import extract_text_from_pdf
from services.resume_analyzer import analyze_resume_text


router = APIRouter(
    prefix="/resumes",
    tags=["Resume Analysis"],
)


@router.post(
    "/{resume_id}/analyze",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def analyze_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    try:
        file_bytes = download_blob(
            container_name=resume.blob_container,
            blob_path=resume.blob_path,
        )

        resume_text = extract_text_from_pdf(file_bytes)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to read resume from Azure Blob Storage",
        ) from exc

    if not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text was extracted from the resume",
        )

    analysis_data = analyze_resume_text(resume_text)

    existing_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.resume_id == resume.id,
            ResumeAnalysis.user_id == current_user.id,
        )
        .order_by(ResumeAnalysis.created_at.desc())
        .first()
    )

    if existing_analysis:
        for field, value in analysis_data.items():
            setattr(existing_analysis, field, value)

        db.commit()
        db.refresh(existing_analysis)

        return existing_analysis

    analysis = ResumeAnalysis(
        resume_id=resume.id,
        user_id=current_user.id,
        **analysis_data,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


@router.get(
    "/{resume_id}/analysis",
    response_model=ResumeAnalysisResponse,
)
def get_resume_analysis(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.resume_id == resume_id,
            ResumeAnalysis.user_id == current_user.id,
        )
        .order_by(ResumeAnalysis.created_at.desc())
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found",
        )

    return analysis