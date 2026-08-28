from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.application import Application
from models.company import Company
from models.application_answer import ApplicationAnswer
from models.application_status_history import (
    ApplicationStatusHistory,
)
from schemas.application import ApplicationResponse
from schemas.application_status_history import (
    ApplicationStatusHistoryCreate,
)
from models.job import Job
from models.job_screening_question import (
    JobScreeningQuestion,
)
from models.profile import Profile
from models.resume import Resume
from models.skill import Skill
from models.user import User
from models.user_skill import UserSkill

from schemas.application import ApplicationResponse
from schemas.recruiter_application import (
    RecruiterApplicationAnswer,
    RecruiterApplicationDetailResponse,
    RecruiterApplicationDetails,
    RecruiterCandidate,
    RecruiterCandidateProfile,
    RecruiterCandidateSkill,
    RecruiterJobSummary,
    RecruiterResumeSummary,
)

from services.azure_blob_download import download_blob


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
# RECRUITER APPLICANT SEARCH / FILTER
# ============================================================

@router.get(
    "/applicants",
)
def get_recruiter_applicants(
    job_id: UUID | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    query = (
        db.query(
            Application,
            User.email.label("candidate_email"),
            Profile.full_name.label("candidate_name"),
            Job.title.label("job_title"),
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .join(
            User,
            User.id == Application.user_id,
        )
        .outerjoin(
            Profile,
            Profile.user_id == Application.user_id,
        )
        .filter(
            Job.posted_by == current_user.id
        )
    )

    if job_id is not None:
        query = query.filter(
            Application.job_id == job_id
        )

    if status_filter:
        normalized_status = (
            status_filter.upper()
        )

        valid_statuses = {
            "APPLIED",
            "SCREENING",
            "ASSESSMENT",
            "INTERVIEW",
            "OFFER",
            "REJECTED",
            "WITHDRAWN",
        }

        if normalized_status in valid_statuses:
            query = query.filter(
                Application.status
                == normalized_status
            )

    if search:
        search_pattern = (
            f"%{search.strip()}%"
        )

        query = query.filter(
            User.email.ilike(search_pattern)
            | Profile.full_name.ilike(
                search_pattern
            )
        )

    rows = (
        query
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )

    results = []

    for (
        application,
        candidate_email,
        candidate_name,
        job_title,
    ) in rows:
        application_status = (
            application.status.value
            if hasattr(
                application.status,
                "value",
            )
            else str(
                application.status
            )
        )

        results.append(
            {
                "id": application.id,
                "job_id": application.job_id,
                "candidate_id": application.user_id,
                "candidate_email": candidate_email,
                "candidate_name": candidate_name,
                "job_title": job_title,
                "status": application_status,
                "resume_id": application.resume_id,
                "applied_at": application.applied_at,
                "updated_at": application.updated_at,
            }
        )

    return results


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
    # 1. Verify application belongs to a job owned
    #    by the current recruiter.
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
    # 3. Load candidate
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
    # 4. Candidate profile
    # --------------------------------------------------------

    profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == candidate.id
        )
        .first()
    )

    profile_response = None

    if profile:
        profile_response = RecruiterCandidateProfile(
            id=profile.id,
            full_name=profile.full_name,
            headline=profile.headline,
            bio=profile.bio,
            location=profile.location,
            years_of_experience=(
                profile.years_of_experience
            ),
        )

    # --------------------------------------------------------
    # 5. Candidate skills
    # --------------------------------------------------------

    skill_rows = (
        db.query(
            UserSkill,
            Skill.name.label("name"),
        )
        .join(
            Skill,
            Skill.id == UserSkill.skill_id,
        )
        .filter(
            UserSkill.user_id == candidate.id
        )
        .order_by(
            Skill.name.asc()
        )
        .all()
    )

    skills_response = [
        RecruiterCandidateSkill(
            skill_id=user_skill.skill_id,
            skill_name=skill_name,
            proficiency=user_skill.proficiency,
            years_experience=(
                user_skill.years_experience
            ),
        )
        for user_skill, skill_name in skill_rows
    ]

    candidate_response = RecruiterCandidate(
        id=candidate.id,
        email=candidate.email,
        profile=profile_response,
        skills=skills_response,
    )

    # --------------------------------------------------------
    # 6. Resume metadata
    #
    # Do not expose blob_container or blob_path.
    # --------------------------------------------------------

    resume_response = None

    if application.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id == application.resume_id,
                Resume.user_id == application.user_id,
            )
            .first()
        )

        if resume:
            resume_response = RecruiterResumeSummary(
                id=resume.id,
                file_name=resume.file_name,
                content_type=resume.content_type,
                file_size_bytes=(
                    resume.file_size_bytes
                ),
                is_primary=resume.is_primary,
            )

    # --------------------------------------------------------
    # 7. Application
    # --------------------------------------------------------

    application_status = (
        application.status.value
        if hasattr(application.status, "value")
        else str(application.status)
    )

    application_response = RecruiterApplicationDetails(
        id=application.id,
        job_id=application.job_id,
        user_id=application.user_id,
        resume_id=application.resume_id,
        status=application_status,
        cover_letter=application.cover_letter,
        applied_at=application.applied_at,
        updated_at=application.updated_at,
    )

    # --------------------------------------------------------
    # 8. Job
    # --------------------------------------------------------

    job_status = (
        job.status.value
        if hasattr(job.status, "value")
        else str(job.status)
    )

    company = (
        db.query(Company)
        .filter(
            Company.id == job.company_id
        )
        .first()
    )

    job_response = RecruiterJobSummary(
        id=job.id,
        company_id=job.company_id,
        company_name=(
            company.name
            if company
            else None
        ),
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
        status=job_status,
    )

    return RecruiterApplicationDetailResponse(
        application=application_response,
        candidate=candidate_response,
        job=job_response,
        resume=resume_response,
    )


# ============================================================
# GET SCREENING ANSWERS FOR AN APPLICANT
#
# Security:
#   RECRUITER
#       +
#   application belongs to a job owned by recruiter
#       ↓
#   ALLOW
# ============================================================

@router.get(
    "/{application_id}/answers",
    response_model=list[RecruiterApplicationAnswer],
)
def get_recruiter_application_answers(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    # --------------------------------------------------------
    # 1. Verify recruiter owns the associated job.
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
    # 2. Load questions and answers.
    #
    # Only answers submitted for this application are
    # returned.
    # --------------------------------------------------------

    rows = (
        db.query(
            ApplicationAnswer.id,
            ApplicationAnswer.question_id,
            JobScreeningQuestion.question,
            JobScreeningQuestion.question_type,
            JobScreeningQuestion.is_required,
            JobScreeningQuestion.display_order,
            ApplicationAnswer.answer,
        )
        .join(
            JobScreeningQuestion,
            JobScreeningQuestion.id
            == ApplicationAnswer.question_id,
        )
        .filter(
            ApplicationAnswer.application_id
            == application_id,
            JobScreeningQuestion.job_id
            == application.job_id,
        )
        .order_by(
            JobScreeningQuestion.display_order.asc(),
            ApplicationAnswer.created_at.asc(),
        )
        .all()
    )

    return [
        RecruiterApplicationAnswer(
            id=row.id,
            question_id=row.question_id,
            question=row.question,
            question_type=row.question_type,
            is_required=row.is_required,
            display_order=row.display_order,
            answer=row.answer,
        )
        for row in rows
    ]


# ============================================================
# UPDATE APPLICATION STATUS
#
# Recruiter controls hiring-stage transitions.
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
    # 1. Verify recruiter owns the job.
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
    # 3. Valid recruiter transitions.
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

    allowed_next_statuses = allowed_transitions.get(
        current_status,
        set(),
    )

    if requested_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Invalid application status transition: "
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
    # 5. Create status history.
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
# DOWNLOAD APPLICANT RESUME
#
# Security:
#   RECRUITER
#       +
#   application belongs to recruiter's own job
#       +
#   resume belongs to the applicant
#       ↓
#   ALLOW
# ============================================================

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
    # --------------------------------------------------------
    # 1. Verify recruiter owns associated job.
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
    # 2. Resume must exist.
    # --------------------------------------------------------

    if not application.resume_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume attached to this application",
        )

    # --------------------------------------------------------
    # 3. Verify resume belongs to candidate.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 4. Download from Azure.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 5. Return file.
    # --------------------------------------------------------

    return StreamingResponse(
        BytesIO(file_bytes),
        media_type=(
            resume.content_type
            or "application/pdf"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{resume.file_name}"'
            )
        },
    )