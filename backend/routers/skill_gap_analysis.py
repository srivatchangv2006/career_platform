from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.job import Job
from models.job_skill import JobSkill
from models.skill import Skill
from models.skill_gap_analysis import SkillGapAnalysis
from models.user import User
from models.user_skill import UserSkill
from schemas.skill_gap_analysis import SkillGapAnalysisResponse
from services.skill_gap_analyzer import analyze_skill_gap


router = APIRouter(
    prefix="/jobs",
    tags=["Skill Gap Analysis"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "/{job_id}/skill-gap",
    response_model=SkillGapAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill_gap_analysis(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

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

    required_skills = (
        db.query(Skill.name)
        .join(
            JobSkill,
            JobSkill.skill_id == Skill.id,
        )
        .filter(
            JobSkill.job_id == job_id,
            JobSkill.is_required.is_(True),
        )
        .all()
    )

    candidate_skill_names = [
        skill[0]
        for skill in candidate_skills
    ]

    required_skill_names = [
        skill[0]
        for skill in required_skills
    ]

    if not required_skill_names:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This job has no required skills defined",
        )

    analysis_data = analyze_skill_gap(
        candidate_skills=candidate_skill_names,
        required_skills=required_skill_names,
    )

    existing_analysis = (
        db.query(SkillGapAnalysis)
        .filter(
            SkillGapAnalysis.user_id == current_user.id,
            SkillGapAnalysis.job_id == job_id,
        )
        .first()
    )

    if existing_analysis:
        existing_analysis.matched_skills = (
            analysis_data["matched_skills"]
        )
        existing_analysis.missing_skills = (
            analysis_data["missing_skills"]
        )
        existing_analysis.recommendations = (
            analysis_data["recommendations"]
        )
        existing_analysis.overall_match_score = (
            analysis_data["overall_match_score"]
        )

        db.commit()
        db.refresh(existing_analysis)

        return existing_analysis

    analysis = SkillGapAnalysis(
        user_id=current_user.id,
        job_id=job_id,
        matched_skills=analysis_data["matched_skills"],
        missing_skills=analysis_data["missing_skills"],
        recommendations=analysis_data["recommendations"],
        overall_match_score=analysis_data["overall_match_score"],
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


@router.get(
    "/{job_id}/skill-gap",
    response_model=SkillGapAnalysisResponse,
)
def get_skill_gap_analysis(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = (
        db.query(SkillGapAnalysis)
        .filter(
            SkillGapAnalysis.user_id == current_user.id,
            SkillGapAnalysis.job_id == job_id,
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill gap analysis not found",
        )

    return analysis