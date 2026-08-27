from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.job import Job, JobStatus
from models.job_preference import JobPreference
from models.job_recommendation_item import JobRecommendationItem
from models.job_recommendation_run import JobRecommendationRun
from models.skill import Skill
from models.user import User
from models.user_skill import UserSkill
from schemas.job_recommendation import (
    JobRecommendationItemResponse,
    JobRecommendationRunResponse,
)
from services.job_recommender import generate_job_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["Job Recommendations"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "/jobs",
    response_model=JobRecommendationRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------
    # 1. Get candidate job preferences
    # --------------------------------------------------

    preferences = (
        db.query(JobPreference)
        .filter(
            JobPreference.user_id == current_user.id
        )
        .first()
    )

    # --------------------------------------------------
    # 2. Get candidate skills
    # --------------------------------------------------

    candidate_skills = (
        db.query(Skill.name)
        .join(
            UserSkill,
            UserSkill.skill_id == Skill.id,
        )
        .filter(
            UserSkill.user_id == current_user.id
        )
        .all()
    )

    candidate_skill_names = [
        skill[0]
        for skill in candidate_skills
    ]

    # --------------------------------------------------
    # 3. Get available OPEN jobs
    # --------------------------------------------------

    jobs = (
        db.query(Job)
        .filter(Job.status == JobStatus.OPEN)
        .all()
    )

    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No open jobs available",
        )

    # --------------------------------------------------
    # 4. Prepare job data for Gemini
    # --------------------------------------------------

    job_data = []

    for job in jobs:
        job_data.append(
            {
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "location": job.location,
                "employment_type": job.employment_type,
                "experience_level": job.experience_level,
                "salary_min": (
                    float(job.salary_min)
                    if job.salary_min is not None
                    else None
                ),
                "salary_max": (
                    float(job.salary_max)
                    if job.salary_max is not None
                    else None
                ),
                "currency": job.currency,
            }
        )

    # --------------------------------------------------
    # 5. Prepare candidate profile for Gemini
    # --------------------------------------------------

    candidate_profile = {
        "skills": candidate_skill_names,
        "preferred_roles": (
            preferences.preferred_roles
            if preferences
            else []
        ),
        "preferred_locations": (
            preferences.preferred_locations
            if preferences
            else []
        ),
        "preferred_employment_types": (
            preferences.preferred_employment_types
            if preferences
            else []
        ),
        "preferred_experience_levels": (
            preferences.preferred_experience_levels
            if preferences
            else []
        ),
        "minimum_salary": (
            float(preferences.minimum_salary)
            if (
                preferences
                and preferences.minimum_salary is not None
            )
            else None
        ),
        "preferred_currency": (
            preferences.preferred_currency
            if preferences
            else "USD"
        ),
        "remote_preferred": (
            preferences.remote_preferred
            if preferences
            else False
        ),
    }

    # --------------------------------------------------
    # 6. Create recommendation run
    # --------------------------------------------------

    run = JobRecommendationRun(
        user_id=current_user.id,
        status="RUNNING",
        input_context=candidate_profile,
        model_name="gemini-3.6-flash",
        started_at=datetime.now(timezone.utc),
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    # --------------------------------------------------
    # 7. Ask Gemini for recommendations
    # --------------------------------------------------

    try:
        recommendations = generate_job_recommendations(
            candidate_profile=candidate_profile,
            jobs=job_data,
        )

        if not recommendations:
            raise RuntimeError(
                "Gemini returned no job recommendations"
            )

        stored_recommendations = []

        # --------------------------------------------------
        # 8. Store recommendation items
        # --------------------------------------------------

        for ranking, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            recommendation_job_id = UUID(
                str(recommendation["job_id"])
            )

            # Verify Gemini returned a job that actually exists
            matching_job = (
                db.query(Job)
                .filter(Job.id == recommendation_job_id)
                .first()
            )

            if not matching_job:
                continue

            match_score = float(
                recommendation["match_score"]
            )

            match_score = max(
                0.0,
                min(100.0, match_score),
            )

            recommendation_reason = str(
                recommendation["recommendation_reason"]
            )

            item = JobRecommendationItem(
                run_id=run.id,
                job_id=recommendation_job_id,
                match_score=match_score,
                recommendation_reason=recommendation_reason,
                ranking=ranking,
            )

            db.add(item)

            # IMPORTANT:
            # JSONB cannot serialize Python UUID objects.
            stored_recommendation = {
                "job_id": str(recommendation_job_id),
                "match_score": match_score,
                "recommendation_reason": recommendation_reason,
            }

            stored_recommendations.append(
                stored_recommendation
            )

        if not stored_recommendations:
            raise RuntimeError(
                "Gemini recommendations did not contain valid jobs"
            )

        # --------------------------------------------------
        # 9. Mark run as completed
        # --------------------------------------------------

        run.status = "COMPLETED"
        run.recommendations = stored_recommendations
        run.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(run)

        return run

    except Exception as exc:
        # IMPORTANT:
        # Reset the failed SQLAlchemy transaction first.
        db.rollback()

        run.status = "FAILED"
        run.error_message = str(exc)
        run.completed_at = datetime.now(timezone.utc)

        db.add(run)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate job recommendations",
        ) from exc


@router.get(
    "/jobs/{run_id}",
    response_model=JobRecommendationRunResponse,
)
def get_recommendation_run(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = (
        db.query(JobRecommendationRun)
        .filter(
            JobRecommendationRun.id == run_id,
            JobRecommendationRun.user_id == current_user.id,
        )
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation run not found",
        )

    return run


@router.get(
    "/jobs/{run_id}/items",
    response_model=list[JobRecommendationItemResponse],
)
def get_recommendation_items(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = (
        db.query(JobRecommendationRun)
        .filter(
            JobRecommendationRun.id == run_id,
            JobRecommendationRun.user_id == current_user.id,
        )
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation run not found",
        )

    return (
        db.query(JobRecommendationItem)
        .filter(
            JobRecommendationItem.run_id == run_id
        )
        .order_by(
            JobRecommendationItem.ranking.asc()
        )
        .all()
    )