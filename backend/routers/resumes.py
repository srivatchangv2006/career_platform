from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.resume import Resume
from models.user import User
from schemas.resume import ResumeResponse
from services.agents import run_resume_agent
from services.ai_status import classify_ai_error

from services.azure_blob import (
    AZURE_STORAGE_CONTAINER_NAME,
    blob_service_client,
    upload_resume,
)


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_user_resume(
    file: UploadFile = File(...),
    resume_name: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resumes are allowed",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file is empty",
        )

    existing_resumes = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id
        )
        .all()
    )

    # The first resume is automatically the default.
    # If the user has resumes but somehow no default,
    # make this upload the default as well.
    has_primary = any(
        resume.is_primary
        for resume in existing_resumes
    )

    is_primary = (
        len(existing_resumes) == 0
        or not has_primary
    )

    display_name = (
        resume_name.strip()
        if resume_name
        and resume_name.strip()
        else (file.filename or "resume.pdf")
    )

    blob_path = upload_resume(
        file_bytes=file_bytes,
        original_filename=file.filename or "resume.pdf",
        content_type=file.content_type,
        user_id=str(current_user.id),
    )

    resume = Resume(
        user_id=current_user.id,
        file_name=display_name,
        blob_container=AZURE_STORAGE_CONTAINER_NAME,
        blob_path=blob_path,
        content_type=file.content_type,
        file_size_bytes=len(file_bytes),
        is_primary=is_primary,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    # --------------------------------------------------------
    # Automatically run Resume Agent
    #
    # The resume is already safely persisted before the agent
    # runs, so an AI failure does not invalidate the upload.
    # --------------------------------------------------------

    ai_analysis_status = "COMPLETED"

    try:
        run_resume_agent(
            db=db,
            user_id=current_user.id,
            resume_id=resume.id,
        )
    except Exception as exc:
        import traceback

        db.rollback()

        ai_analysis_status = classify_ai_error(
            exc
        )

        print(
            "RESUME AGENT FAILED:",
            type(exc).__name__,
            str(exc),
        )
        traceback.print_exc()

    db.refresh(resume)

    response_data = ResumeResponse.model_validate(
        resume
    )

    response_data.ai_analysis_status = (
        ai_analysis_status
    )

    return response_data


@router.get(
    "/me",
    response_model=list[ResumeResponse],
)
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(
            Resume.is_primary.desc(),
            Resume.created_at.desc(),
        )
        .all()
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
)
def get_resume(
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

    return resume


@router.post(
    "/{resume_id}/primary",
    response_model=ResumeResponse,
)
def set_primary_resume(
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

    db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.id != resume_id,
    ).update(
        {"is_primary": False},
        synchronize_session=False,
    )

    resume.is_primary = True

    db.commit()
    db.refresh(resume)

    return resume


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resume(
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
        blob_client = blob_service_client.get_blob_client(
            container=resume.blob_container,
            blob=resume.blob_path,
        )

        if blob_client.exists():
            blob_client.delete_blob()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to delete resume from Azure Blob Storage",
        ) from exc

    db.delete(resume)
    db.commit()

    return None