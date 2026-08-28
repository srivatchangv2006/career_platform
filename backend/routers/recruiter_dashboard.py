from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.application import Application
from models.interview import Interview
from models.job import Job
from models.profile import Profile
from models.user import User

from schemas.recruiter_dashboard import (
    RecruiterApplicationListItem,
    RecruiterApplicationStatusCounts,
    RecruiterDashboardResponse,
)


router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter Dashboard"],
)


# ============================================================
# RECRUITER DASHBOARD
#
# Only data belonging to jobs owned by the current recruiter
# is included.
# ============================================================

@router.get(
    "/dashboard",
    response_model=RecruiterDashboardResponse,
)
def get_recruiter_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    # --------------------------------------------------------
    # Jobs owned by recruiter
    # --------------------------------------------------------

    recruiter_jobs = (
        db.query(Job)
        .filter(
            Job.posted_by == current_user.id
        )
        .all()
    )

    total_jobs = len(recruiter_jobs)

    open_jobs = sum(
        1
        for job in recruiter_jobs
        if (
            job.status.value
            if hasattr(job.status, "value")
            else str(job.status)
        ) == "OPEN"
    )

    # --------------------------------------------------------
    # Applications belonging to those jobs
    # --------------------------------------------------------

    applications = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Job.posted_by == current_user.id
        )
        .all()
    )

    status_counts = {
        "APPLIED": 0,
        "SCREENING": 0,
        "ASSESSMENT": 0,
        "INTERVIEW": 0,
        "OFFER": 0,
        "REJECTED": 0,
        "WITHDRAWN": 0,
    }

    for application in applications:
        current_status = (
            application.status.value
            if hasattr(
                application.status,
                "value",
            )
            else str(application.status)
        )

        if current_status in status_counts:
            status_counts[current_status] += 1

    # --------------------------------------------------------
    # Upcoming interviews for recruiter's applications
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    upcoming_interviews = (
        db.query(Interview)
        .join(
            Application,
            Application.id
            == Interview.application_id,
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Job.posted_by == current_user.id,
            Interview.scheduled_at.isnot(None),
            Interview.scheduled_at >= now,
            Interview.status.notin_(
                ["CANCELLED", "COMPLETED"]
            ),
        )
        .count()
    )

    return RecruiterDashboardResponse(
        total_jobs=total_jobs,
        open_jobs=open_jobs,
        total_applications=len(applications),
        applications_by_status=(
            RecruiterApplicationStatusCounts(
                **status_counts
            )
        ),
        upcoming_interviews=upcoming_interviews,
    )


# ============================================================
# RECRUITER APPLICANT SEARCH / FILTER
#
# Supported filters:
#   job_id
#   status
#   search
#
# Security:
#   Recruiter can ONLY see applications attached to jobs
#   owned by that recruiter.
# ============================================================

@router.get(
    "/applicants",
    response_model=list[RecruiterApplicationListItem],
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

    # --------------------------------------------------------
    # Job filter
    # --------------------------------------------------------

    if job_id is not None:
        query = query.filter(
            Application.job_id == job_id
        )

    # --------------------------------------------------------
    # Status filter
    # --------------------------------------------------------

    if status_filter:
        normalized_status = status_filter.upper()

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

    # --------------------------------------------------------
    # Candidate search
    # --------------------------------------------------------

    if search:
        search_pattern = f"%{search.strip()}%"

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

    for application, candidate_email, candidate_name, job_title in rows:
        application_status = (
            application.status.value
            if hasattr(
                application.status,
                "value",
            )
            else str(application.status)
        )

        results.append(
            RecruiterApplicationListItem(
                id=application.id,
                job_id=application.job_id,
                candidate_id=application.user_id,
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                job_title=job_title,
                status=application_status,
                resume_id=application.resume_id,
                applied_at=application.applied_at,
                updated_at=application.updated_at,
            )
        )

    return results
