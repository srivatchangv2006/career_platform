from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role

from models.job import Job
from models.job_skill import JobSkill
from models.skill import Skill
from models.user import User

from schemas.job_skill import (
    JobSkillCreate,
    JobSkillResponse,
    JobSkillUpdate,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Job Skills"],
)


# ==================================================
# Recruiter/Admin: Add Skill to Own Job
# ==================================================

@router.post(
    "/{job_id}/skills",
    response_model=JobSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_job_skill(
    job_id: UUID,
    skill_data: JobSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    skill = (
        db.query(Skill)
        .filter(
            Skill.id == skill_data.skill_id
        )
        .first()
    )

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    existing_job_skill = (
        db.query(JobSkill)
        .filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id
            == skill_data.skill_id,
        )
        .first()
    )

    if existing_job_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill already added to this job",
        )

    job_skill = JobSkill(
        job_id=job_id,
        **skill_data.model_dump(),
    )

    db.add(job_skill)
    db.commit()
    db.refresh(job_skill)

    return job_skill


# ==================================================
# Shared: View Job Skills
# ==================================================

@router.get(
    "/{job_id}/skills",
    response_model=list[JobSkillResponse],
)
def get_job_skills(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return (
        db.query(JobSkill)
        .filter(
            JobSkill.job_id == job_id
        )
        .order_by(
            JobSkill.created_at.asc()
        )
        .all()
    )


# ==================================================
# Recruiter/Admin: Update Skill on Own Job
# ==================================================

@router.put(
    "/{job_id}/skills/{skill_id}",
    response_model=JobSkillResponse,
)
def update_job_skill(
    job_id: UUID,
    skill_id: UUID,
    skill_data: JobSkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    job_skill = (
        db.query(JobSkill)
        .filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_id,
        )
        .first()
    )

    if not job_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job skill not found",
        )

    update_data = skill_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            job_skill,
            field,
            value,
        )

    db.commit()
    db.refresh(job_skill)

    return job_skill


# ==================================================
# Recruiter/Admin: Delete Skill from Own Job
# ==================================================

@router.delete(
    "/{job_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job_skill(
    job_id: UUID,
    skill_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    job_skill = (
        db.query(JobSkill)
        .filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_id,
        )
        .first()
    )

    if not job_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job skill not found",
        )

    db.delete(job_skill)
    db.commit()

    return None