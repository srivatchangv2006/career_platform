from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.application import Application
from models.application_status_history import (
    ApplicationStatusHistory,
)
from models.interview import Interview
from models.interview_preparation import InterviewPreparation
from models.job_recommendation_item import (
    JobRecommendationItem,
)
from models.job_recommendation_run import (
    JobRecommendationRun,
)
from models.skill_gap_analysis import SkillGapAnalysis
from models.user import User

from schemas.application_timeline import (
    ApplicationTimelineEvent,
    ApplicationTimelineResponse,
)


router = APIRouter(
    prefix="/applications",
    tags=["Application Timeline"],
)


def enum_value(value) -> str | None:
    if value is None:
        return None

    return (
        value.value
        if hasattr(value, "value")
        else str(value)
    )


@router.get(
    "/{application_id}/timeline",
    response_model=ApplicationTimelineResponse,
)
def get_application_timeline(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    events: list[ApplicationTimelineEvent] = []

    # -------------------------------------------------
    # Application submitted
    # -------------------------------------------------

    if application.applied_at:
        application_status = enum_value(
            application.status
        )

        events.append(
            ApplicationTimelineEvent(
                id=application.id,
                event_type="APPLICATION_SUBMITTED",
                title="Application submitted",
                description=(
                    "Application was submitted "
                    "for this job."
                ),
                status=application_status,
                created_at=application.applied_at,
            )
        )

    # -------------------------------------------------
    # Status history
    # -------------------------------------------------

    status_history = (
        db.query(ApplicationStatusHistory)
        .filter(
            ApplicationStatusHistory.application_id
            == application_id
        )
        .order_by(
            ApplicationStatusHistory.created_at.asc()
        )
        .all()
    )

    for history in status_history:
        history_status = enum_value(
            history.status
        )

        events.append(
            ApplicationTimelineEvent(
                id=history.id,
                event_type="STATUS_CHANGED",
                title=(
                    "Application status changed to "
                    f"{history_status}"
                ),
                description=history.notes,
                status=history_status,
                created_at=history.created_at,
            )
        )

    # -------------------------------------------------
    # Skill gap analysis
    # -------------------------------------------------

    skill_gap = (
        db.query(SkillGapAnalysis)
        .filter(
            SkillGapAnalysis.user_id
            == current_user.id,
            SkillGapAnalysis.job_id
            == application.job_id,
        )
        .order_by(
            SkillGapAnalysis.created_at.asc()
        )
        .first()
    )

    if skill_gap:
        events.append(
            ApplicationTimelineEvent(
                id=skill_gap.id,
                event_type="SKILL_GAP_ANALYSIS",
                title="Skill gap analysis completed",
                description=(
                    "AI skill-gap analysis was "
                    "generated for this job."
                ),
                status=None,
                created_at=skill_gap.created_at,
            )
        )

    # -------------------------------------------------
    # Job recommendation runs
    # -------------------------------------------------

    recommendation_runs = (
        db.query(JobRecommendationRun)
        .filter(
            JobRecommendationRun.user_id
            == current_user.id
        )
        .order_by(
            JobRecommendationRun.created_at.asc()
        )
        .all()
    )

    for run in recommendation_runs:
        recommendation_item = (
            db.query(JobRecommendationItem)
            .filter(
                JobRecommendationItem.run_id
                == run.id,
                JobRecommendationItem.job_id
                == application.job_id,
            )
            .first()
        )

        if recommendation_item:
            events.append(
                ApplicationTimelineEvent(
                    id=run.id,
                    event_type="JOB_RECOMMENDATION",
                    title=(
                        "Job recommendation generated"
                    ),
                    description=(
                        "This job was included in an "
                        "AI-generated job recommendation."
                    ),
                    status=enum_value(run.status),
                    created_at=run.created_at,
                )
            )

    # -------------------------------------------------
    # Interviews
    # -------------------------------------------------

    interviews = (
        db.query(Interview)
        .filter(
            Interview.application_id
            == application_id
        )
        .order_by(
            Interview.created_at.asc()
        )
        .all()
    )

    for interview in interviews:
        events.append(
            ApplicationTimelineEvent(
                id=interview.id,
                event_type="INTERVIEW_CREATED",
                title="Interview scheduled",
                description=(
                    f"{interview.interview_type} "
                    "interview was scheduled."
                ),
                status=interview.status,
                created_at=interview.created_at,
            )
        )

    # -------------------------------------------------
    # Interview preparation
    # -------------------------------------------------

    preparations = (
        db.query(InterviewPreparation)
        .filter(
            InterviewPreparation.application_id
            == application_id,
            InterviewPreparation.user_id
            == current_user.id,
        )
        .order_by(
            InterviewPreparation.created_at.asc()
        )
        .all()
    )

    for preparation in preparations:
        events.append(
            ApplicationTimelineEvent(
                id=preparation.id,
                event_type="INTERVIEW_PREPARATION",
                title=(
                    "Interview preparation generated"
                ),
                description=(
                    "AI interview preparation was "
                    "generated for this application."
                ),
                status=None,
                created_at=preparation.created_at,
            )
        )

    # -------------------------------------------------
    # Sort chronologically
    # -------------------------------------------------

    events.sort(
        key=lambda event: event.created_at
    )

    return ApplicationTimelineResponse(
        application_id=application_id,
        events=events,
    )