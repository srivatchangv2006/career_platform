from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from models.application_status_history import (ApplicationStatusHistory,)
from dependencies import get_db
from dependencies.roles import require_role

from models.application import Application
from models.job import Job
from models.profile import Profile
from models.resume import Resume
from models.skill import Skill
from models.user import User
from models.user_skill import UserSkill
from schemas.application_status_history import (
    ApplicationStatusHistoryCreate,
)
from fastapi.responses import StreamingResponse
from io import BytesIO

from services.azure_blob_download import download_blob
from schemas.application import ApplicationResponse
from schemas.recruiter_application import (
    RecruiterApplicationDetailResponse,
    RecruiterApplicationDetails,
    RecruiterCandidate,
    RecruiterCandidateProfile,
    RecruiterCandidateSkill,
    RecruiterJobSummary,
    RecruiterResumeSummary,
)


router = APIRouter(
    prefix="/recruiter/applications",
    tags=["Recruiter Applications"],
)


# ============================================================
# GET ALL APPLICATIONS FOR JOBS OWNED BY CURRENT RECRUITER
# ============================================================

@router.get(
    "",
    response_model=list[ApplicationResponse],
)
def get_recruiter_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    applications = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Job.posted_by == current_user.id
        )
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )

    return applications


# ============================================================
# GET A SINGLE APPLICATION
#
# Recruiter can only see an application if the associated
# job belongs to that recruiter.
# ============================================================

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_recruiter_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    application = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application


# ============================================================
# GET DETAILED APPLICANT INFORMATION
#
# Security:
#   1. User must be a RECRUITER.
#   2. Recruiter must own the job associated with the
#      application.
#
# Candidate information is read-only here.
# Password/authentication data is never returned.
# ============================================================

@router.get(
    "/{application_id}/details",
    response_model=RecruiterApplicationDetailResponse,
)
def get_recruiter_application_details(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    # --------------------------------------------------------
    # 1. Find application + ensure recruiter owns the job
    # --------------------------------------------------------

    application = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # --------------------------------------------------------
    # 2. Load job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # --------------------------------------------------------
    # 3. Load candidate user
    # --------------------------------------------------------

    candidate = (
        db.query(User)
        .filter(
            User.id == application.user_id
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    # --------------------------------------------------------
    # 4. Load candidate profile
    # --------------------------------------------------------

    profile = (
        db.query(Profile)
        .filter(
            Profile.user_id
            == candidate.id
        )
        .first()
    )

    profile_response = None

    if profile:
        profile_response = (
            RecruiterCandidateProfile(
                id=profile.id,
                full_name=profile.full_name,
                headline=profile.headline,
                bio=profile.bio,
                location=profile.location,
                years_of_experience=(
                    profile.years_of_experience
                ),
            )
        )

    # --------------------------------------------------------
    # 5. Load candidate skills
    # --------------------------------------------------------

    skill_rows = (
        db.query(UserSkill)
        .join(
            Skill,
            Skill.id == UserSkill.skill_id,
        )
        .filter(
            UserSkill.user_id
            == candidate.id
        )
        .order_by(
            Skill.name.asc()
        )
        .all()
    )

    skills_response = [
        RecruiterCandidateSkill(
            skill_id=row.skill_id,
            proficiency=row.proficiency,
            years_experience=(
                row.years_experience
            ),
        )
        for row in skill_rows
    ]

    # --------------------------------------------------------
    # 6. Candidate object
    # --------------------------------------------------------

    candidate_response = RecruiterCandidate(
        id=candidate.id,
        email=candidate.email,
        profile=profile_response,
        skills=skills_response,
    )

    # --------------------------------------------------------
    # 7. Resume
    #
    # Only return safe resume metadata.
    # Do not expose blob_container/blob_path.
    # --------------------------------------------------------

    resume_response = None

    if application.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id
                == application.resume_id,
                Resume.user_id
                == application.user_id,
            )
            .first()
        )

        if resume:
            resume_response = (
                RecruiterResumeSummary(
                    id=resume.id,
                    file_name=resume.file_name,
                    content_type=resume.content_type,
                    file_size_bytes=(
                        resume.file_size_bytes
                    ),
                    is_primary=resume.is_primary,
                )
            )

    # --------------------------------------------------------
    # 8. Application
    # --------------------------------------------------------

    application_response = (
        RecruiterApplicationDetails(
            id=application.id,
            job_id=application.job_id,
            user_id=application.user_id,
            resume_id=application.resume_id,
            status=(
                application.status.value
                if hasattr(
                    application.status,
                    "value",
                )
                else str(application.status)
            ),
            cover_letter=application.cover_letter,
            applied_at=application.applied_at,
            updated_at=application.updated_at,
        )
    )

    # --------------------------------------------------------
    # 9. Job
    # --------------------------------------------------------

    job_response = RecruiterJobSummary(
        id=job.id,
        company_id=job.company_id,
        title=job.title,
        description=job.description,
        location=job.location,
        employment_type=job.employment_type,
        experience_level=job.experience_level,
        salary_min=(
            float(job.salary_min)
            if job.salary_min is not None
            else None
        ),
        salary_max=(
            float(job.salary_max)
            if job.salary_max is not None
            else None
        ),
        currency=job.currency,
        status=(
            job.status.value
            if hasattr(
                job.status,
                "value",
            )
            else str(job.status)
        ),
    )

    # --------------------------------------------------------
    # 10. Final response
    # --------------------------------------------------------

    return RecruiterApplicationDetailResponse(
        application=application_response,
        candidate=candidate_response,
        job=job_response,
        resume=resume_response,
    )
# ============================================================
# RECRUITER: UPDATE APPLICATION STATUS
#
# Security:
#   1. User must be a RECRUITER.
#   2. Recruiter must own the job associated with the
#      application.
#   3. The requested status transition must be valid.
#   4. Every successful change creates an application
#      status-history record.
# ============================================================

@router.put(
    "/{application_id}/status",
    response_model=ApplicationResponse,
)
def update_recruiter_application_status(
    application_id: UUID,
    status_data: ApplicationStatusHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    # --------------------------------------------------------
    # 1. Find application belonging to a job owned by
    #    the current recruiter.
    # --------------------------------------------------------

    application = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # --------------------------------------------------------
    # 2. Get current and requested statuses.
    # --------------------------------------------------------

    current_status = (
        application.status.value
        if hasattr(
            application.status,
            "value",
        )
        else str(application.status)
    )

    requested_status = (
        status_data.status.value
        if hasattr(
            status_data.status,
            "value",
        )
        else str(status_data.status)
    )

    # --------------------------------------------------------
    # 3. Allowed recruiter transitions.
    # --------------------------------------------------------

    allowed_transitions = {
        "APPLIED": {
            "SCREENING",
            "REJECTED",
        },
        "SCREENING": {
            "ASSESSMENT",
            "INTERVIEW",
            "REJECTED",
        },
        "ASSESSMENT": {
            "INTERVIEW",
            "REJECTED",
        },
        "INTERVIEW": {
            "OFFER",
            "REJECTED",
        },
        "OFFER": {
            "REJECTED",
        },
    }

    # --------------------------------------------------------
    # 4. Reject invalid transitions.
    # --------------------------------------------------------

    allowed_next_statuses = allowed_transitions.get(
        current_status,
        set(),
    )

    if requested_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid application status transition: "
                f"{current_status} -> {requested_status}"
            ),
        )

    # --------------------------------------------------------
    # 5. Update application status.
    # --------------------------------------------------------

    application.status = status_data.status
    application.updated_at = datetime.now(
        timezone.utc
    )

    # --------------------------------------------------------
    # 6. Create status-history record.
    # --------------------------------------------------------

    history = ApplicationStatusHistory(
        application_id=application.id,
        status=status_data.status,
        changed_by=current_user.id,
        notes=status_data.notes,
    )

    db.add(history)

    db.commit()
    db.refresh(application)

    return application
# ============================================================
# RECRUITER: UPDATE APPLICATION STATUS
# ============================================================

@router.put(
    "/{application_id}/status",
    response_model=ApplicationResponse,
)
def update_recruiter_application_status(
    application_id: UUID,
    status_data: ApplicationStatusHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    # --------------------------------------------------------
    # 1. Find application and verify that the recruiter
    #    owns the associated job.
    # --------------------------------------------------------

    application = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # --------------------------------------------------------
    # 2. Normalize statuses.
    # --------------------------------------------------------

    current_status = (
        application.status.value
        if hasattr(application.status, "value")
        else str(application.status)
    )

    requested_status = (
        status_data.status.value
        if hasattr(status_data.status, "value")
        else str(status_data.status)
    )

    # --------------------------------------------------------
    # 3. Recruiter-controlled workflow.
    # --------------------------------------------------------

    allowed_transitions = {
        "APPLIED": {
            "SCREENING",
            "REJECTED",
        },
        "SCREENING": {
            "ASSESSMENT",
            "INTERVIEW",
            "REJECTED",
        },
        "ASSESSMENT": {
            "INTERVIEW",
            "REJECTED",
        },
        "INTERVIEW": {
            "OFFER",
            "REJECTED",
        },
    }

    allowed_next_statuses = allowed_transitions.get(
        current_status,
        set(),
    )

    if requested_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid application status transition: "
                f"{current_status} -> {requested_status}"
            ),
        )

    # --------------------------------------------------------
    # 4. Update application.
    # --------------------------------------------------------

    application.status = status_data.status
    application.updated_at = datetime.now(
        timezone.utc
    )

    # --------------------------------------------------------
    # 5. Record status history.
    # --------------------------------------------------------

    history = ApplicationStatusHistory(
        application_id=application.id,
        status=status_data.status,
        changed_by=current_user.id,
        notes=status_data.notes,
    )

    db.add(history)

    db.commit()
    db.refresh(application)

    return application

@router.get(
    "/{application_id}/resume",
)
def download_recruiter_resume(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    application = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if not application.resume_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume attached to this application",
        )

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == application.resume_id,
            Resume.user_id == application.user_id,
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
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to download resume",
        ) from exc

    return StreamingResponse(
        BytesIO(file_bytes),
        media_type=resume.content_type or "application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{resume.file_name}"'
            )
        },
    )