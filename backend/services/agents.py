from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models.job import Job, JobStatus
from models.job_skill import JobSkill
from models.job_preference import JobPreference
from models.job_recommendation_item import JobRecommendationItem
from models.job_recommendation_run import JobRecommendationRun
from models.resume import Resume
from models.resume_analysis import ResumeAnalysis
from models.skill import Skill
from models.skill_gap_analysis import SkillGapAnalysis
from models.user_skill import UserSkill

from services.azure_blob_download import download_blob
from services.job_recommender import generate_job_recommendations
from services.pdf_extractor import extract_text_from_pdf
from services.resume_analyzer import analyze_resume_text
from services.skill_gap_analyzer import analyze_skill_gap

def run_resume_agent(
    db: Session,
    user_id: UUID,
    resume_id: UUID,
) -> dict:
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
        .first()
    )

    if not resume:
        raise ValueError("Resume not found")

    file_bytes = download_blob(
        container_name=resume.blob_container,
        blob_path=resume.blob_path,
    )

    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text.strip():
        raise ValueError(
            "No readable text found in resume"
        )

    analysis_data = analyze_resume_text(
        resume_text
    )

    existing_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.resume_id == resume.id,
            ResumeAnalysis.user_id == user_id,
        )
        .order_by(
            ResumeAnalysis.created_at.desc()
        )
        .first()
    )

    if existing_analysis:
        for field, value in analysis_data.items():
            setattr(
                existing_analysis,
                field,
                value,
            )

        db.commit()
        db.refresh(existing_analysis)

        analysis = existing_analysis

    else:
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            user_id=user_id,
            **analysis_data,
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

    return {
        "agent": "resume_agent",
        "status": "COMPLETED",
        "resume_id": str(resume.id),
        "analysis_id": str(analysis.id),
        "summary": analysis.summary,
        "extracted_skills": analysis.extracted_skills,
        "recommendations": analysis.recommendations,
    }


def run_skill_gap_agent(
    db: Session,
    user_id: UUID,
    job_id: UUID,
) -> dict:
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise ValueError("Job not found")

    candidate_skills = (
        db.query(Skill.name)
        .join(
            UserSkill,
            UserSkill.skill_id == Skill.id,
        )
        .filter(
            UserSkill.user_id == user_id
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
        raise ValueError(
            "Job has no required skills"
        )

    analysis_data = analyze_skill_gap(
        candidate_skills=candidate_skill_names,
        required_skills=required_skill_names,
    )

    existing_analysis = (
        db.query(SkillGapAnalysis)
        .filter(
            SkillGapAnalysis.user_id == user_id,
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

        analysis = existing_analysis

    else:
        analysis = SkillGapAnalysis(
            user_id=user_id,
            job_id=job_id,
            matched_skills=analysis_data["matched_skills"],
            missing_skills=analysis_data["missing_skills"],
            recommendations=analysis_data["recommendations"],
            overall_match_score=analysis_data[
                "overall_match_score"
            ],
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

    return {
        "agent": "skill_gap_agent",
        "status": "COMPLETED",
        "job_id": str(job_id),
        "analysis_id": str(analysis.id),
        "matched_skills": analysis.matched_skills,
        "missing_skills": analysis.missing_skills,
        "overall_match_score": (
            float(analysis.overall_match_score)
            if analysis.overall_match_score is not None
            else None
        ),
        "recommendations": analysis.recommendations,
    }

def run_job_recommendation_agent(
    db: Session,
    user_id: UUID,
) -> dict:
    preferences = (
        db.query(JobPreference)
        .filter(
            JobPreference.user_id == user_id
        )
        .first()
    )

    candidate_skills = (
        db.query(Skill.name)
        .join(
            UserSkill,
            UserSkill.skill_id == Skill.id,
        )
        .filter(
            UserSkill.user_id == user_id
        )
        .all()
    )

    candidate_skill_names = [
        skill[0]
        for skill in candidate_skills
    ]

    jobs = (
        db.query(Job)
        .filter(Job.status == JobStatus.OPEN)
        .all()
    )

    if not jobs:
        raise ValueError("No open jobs available")

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

    run = JobRecommendationRun(
        user_id=user_id,
        status="RUNNING",
        input_context=candidate_profile,
        model_name="gemini-3.6-flash",
        started_at=datetime.now(timezone.utc),
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        recommendations = generate_job_recommendations(
            candidate_profile=candidate_profile,
            jobs=job_data,
        )

        if not recommendations:
            raise ValueError(
                "Gemini returned no recommendations"
            )

        stored_recommendations = []

        for ranking, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            job_id = UUID(
                str(recommendation["job_id"])
            )

            # Make sure Gemini only recommends a real job
            valid_job = (
                db.query(Job)
                .filter(Job.id == job_id)
                .first()
            )

            if not valid_job:
                continue

            score = max(
                0.0,
                min(
                    100.0,
                    float(
                        recommendation["match_score"]
                    ),
                ),
            )

            reason = str(
                recommendation[
                    "recommendation_reason"
                ]
            )

            item = JobRecommendationItem(
                run_id=run.id,
                job_id=job_id,
                match_score=score,
                recommendation_reason=reason,
                ranking=ranking,
            )

            db.add(item)

            stored_recommendations.append(
                {
                    "job_id": str(job_id),
                    "match_score": score,
                    "recommendation_reason": reason,
                }
            )

        if not stored_recommendations:
            raise ValueError(
                "No valid job recommendations were returned"
            )

        run.status = "COMPLETED"
        run.recommendations = stored_recommendations
        run.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(run)

        return {
            "agent": "job_recommendation_agent",
            "status": "COMPLETED",
            "run_id": str(run.id),
            "recommendations": stored_recommendations,
        }

    except Exception as exc:
        db.rollback()

        run.status = "FAILED"
        run.error_message = str(exc)
        run.completed_at = datetime.now(timezone.utc)

        db.add(run)
        db.commit()

        raise