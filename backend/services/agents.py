from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models.job import Job, JobStatus
from models.job_preference import JobPreference
from models.job_recommendation_item import JobRecommendationItem
from models.job_recommendation_run import JobRecommendationRun
from models.job_skill import JobSkill
from models.resume import Resume
from models.resume_analysis import ResumeAnalysis
from models.skill import Skill
from models.skill_gap_analysis import SkillGapAnalysis
from models.user_skill import UserSkill

from services.ai_interaction_service import log_ai_interaction
from services.azure_blob_download import download_blob
from services.job_recommender import (
    generate_job_recommendations,
)
from services.memory_service import (
    create_or_update_memory,
    search_user_memories,
)
from services.pdf_extractor import extract_text_from_pdf
from services.resume_analyzer import analyze_resume_text
from services.skill_gap_analyzer import analyze_skill_gap


def get_candidate_memory_context(
    db: Session,
    user_id: UUID,
) -> list[dict]:

    return search_user_memories(
        db=db,
        user_id=user_id,
        query=(
            "candidate career preferences, "
            "career goals, skills, job preferences, "
            "professional background, previous "
            "career recommendations, and career "
            "development needs"
        ),
        limit=5,
    )


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
        raise ValueError(
            "Resume not found"
        )

    file_bytes = download_blob(
        container_name=resume.blob_container,
        blob_path=resume.blob_path,
    )

    resume_text = extract_text_from_pdf(
        file_bytes
    )

    if not resume_text.strip():
        raise ValueError(
            "No readable text found in resume"
        )

    memory_context = get_candidate_memory_context(
        db=db,
        user_id=user_id,
    )

    analysis_data = analyze_resume_text(
        resume_text,
        memory_context=memory_context,
    )

    log_ai_interaction(
        db=db,
        user_id=user_id,
        interaction_type="RESUME_ANALYSIS",
        input_text=resume_text,
        output_text=str(analysis_data),
        model_name="gemini-3.6-flash",
        metadata={
            "agent": "resume_agent",
            "resume_id": str(resume_id),
        },
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

    extracted_skills = analysis_data.get(
        "extracted_skills",
        [],
    )

    if extracted_skills:
        create_or_update_memory(
            db=db,
            user_id=user_id,
            memory_type="SKILLS",
            memory_key="resume_extracted_skills",
            memory_value={
                "skills": extracted_skills,
            },
            source="resume_analysis",
            confidence_score=95,
        )

    experience_summary = analysis_data.get(
        "experience_summary",
        [],
    )

    if experience_summary:
        create_or_update_memory(
            db=db,
            user_id=user_id,
            memory_type="EXPERIENCE",
            memory_key="resume_experience",
            memory_value={
                "experience": experience_summary,
            },
            source="resume_analysis",
            confidence_score=90,
        )

    education_summary = analysis_data.get(
        "education_summary",
        [],
    )

    if education_summary:
        create_or_update_memory(
            db=db,
            user_id=user_id,
            memory_type="EDUCATION",
            memory_key="resume_education",
            memory_value={
                "education": education_summary,
            },
            source="resume_analysis",
            confidence_score=90,
        )

    recommendations = analysis_data.get(
        "recommendations",
        [],
    )

    if recommendations:
        create_or_update_memory(
            db=db,
            user_id=user_id,
            memory_type="CAREER_DEVELOPMENT",
            memory_key="resume_recommendations",
            memory_value={
                "recommendations": recommendations,
            },
            source="resume_analysis",
            confidence_score=85,
        )

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
        .filter(
            Job.id == job_id
        )
        .first()
    )

    if not job:
        raise ValueError(
            "Job not found"
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

    log_ai_interaction(
        db=db,
        user_id=user_id,
        interaction_type="SKILL_GAP_ANALYSIS",
        input_text=str(
            {
                "candidate_skills": candidate_skill_names,
                "required_skills": required_skill_names,
                "job_id": str(job_id),
            }
        ),
        output_text=str(analysis_data),
        model_name="gemini-3.6-flash",
        metadata={
            "agent": "skill_gap_agent",
            "job_id": str(job_id),
        },
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
            analysis_data[
                "matched_skills"
            ]
        )

        existing_analysis.missing_skills = (
            analysis_data[
                "missing_skills"
            ]
        )

        existing_analysis.recommendations = (
            analysis_data[
                "recommendations"
            ]
        )

        existing_analysis.overall_match_score = (
            analysis_data[
                "overall_match_score"
            ]
        )

        db.commit()
        db.refresh(existing_analysis)

        analysis = existing_analysis

    else:
        analysis = SkillGapAnalysis(
            user_id=user_id,
            job_id=job_id,
            matched_skills=(
                analysis_data[
                    "matched_skills"
                ]
            ),
            missing_skills=(
                analysis_data[
                    "missing_skills"
                ]
            ),
            recommendations=(
                analysis_data[
                    "recommendations"
                ]
            ),
            overall_match_score=(
                analysis_data[
                    "overall_match_score"
                ]
            ),
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

    missing_skills = analysis_data.get(
        "missing_skills",
        [],
    )

    skill_gap_recommendations = (
        analysis_data.get(
            "recommendations",
            [],
        )
    )

    if (
        missing_skills
        or skill_gap_recommendations
    ):
        create_or_update_memory(
            db=db,
            user_id=user_id,
            memory_type="SKILL_GAP",
            memory_key=(
                f"job_{job_id}_missing_skills"
            ),
            memory_value={
                "job_id": str(job_id),
                "missing_skills": (
                    missing_skills
                ),
                "recommendations": (
                    skill_gap_recommendations
                ),
            },
            source="skill_gap_analysis",
            confidence_score=90,
        )

    return {
        "agent": "skill_gap_agent",
        "status": "COMPLETED",
        "job_id": str(job_id),
        "analysis_id": str(
            analysis.id
        ),
        "matched_skills": (
            analysis.matched_skills
        ),
        "missing_skills": (
            analysis.missing_skills
        ),
        "overall_match_score": (
            float(
                analysis.overall_match_score
            )
            if analysis.overall_match_score
            is not None
            else None
        ),
        "recommendations": (
            analysis.recommendations
        ),
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

    memory_context = (
        get_candidate_memory_context(
            db=db,
            user_id=user_id,
        )
    )

    jobs = (
        db.query(Job)
        .filter(
            Job.status == JobStatus.OPEN
        )
        .all()
    )

    if not jobs:
        raise ValueError(
            "No open jobs available"
        )

    job_data = []

    for job in jobs:
        job_data.append(
            {
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "location": job.location,
                "employment_type": (
                    job.employment_type
                ),
                "experience_level": (
                    job.experience_level
                ),
                "salary_min": (
                    float(job.salary_min)
                    if job.salary_min
                    is not None
                    else None
                ),
                "salary_max": (
                    float(job.salary_max)
                    if job.salary_max
                    is not None
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
            float(
                preferences.minimum_salary
            )
            if (
                preferences
                and preferences.minimum_salary
                is not None
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
        "memory_context": memory_context,
    }

    run = JobRecommendationRun(
        user_id=user_id,
        status="RUNNING",
        input_context=candidate_profile,
        model_name="gemini-3.6-flash",
        started_at=datetime.now(
            timezone.utc
        ),
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    try:

        recommendations = (
            generate_job_recommendations(
                candidate_profile=(
                    candidate_profile
                ),
                jobs=job_data,
            )
        )

        log_ai_interaction(
            db=db,
            user_id=user_id,
            interaction_type=(
                "JOB_RECOMMENDATION"
            ),
            input_text=str(
                {
                    "candidate_profile": candidate_profile,
                    "jobs": job_data,
                }
            ),
            output_text=str(
                recommendations
            ),
            model_name="gemini-3.6-flash",
            metadata={
                "agent": (
                    "job_recommendation_agent"
                ),
            },
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
                str(
                    recommendation[
                        "job_id"
                    ]
                )
            )

            valid_job = (
                db.query(Job)
                .filter(
                    Job.id == job_id
                )
                .first()
            )

            if not valid_job:
                continue

            score = max(
                0.0,
                min(
                    100.0,
                    float(
                        recommendation[
                            "match_score"
                        ]
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
                    "recommendation_reason": (
                        reason
                    ),
                }
            )

        if not stored_recommendations:
            raise ValueError(
                "No valid job recommendations "
                "were returned"
            )

        run.status = "COMPLETED"
        run.recommendations = (
            stored_recommendations
        )
        run.completed_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(run)

        create_or_update_memory(
            db=db,
            user_id=user_id,
            memory_type="JOB_RECOMMENDATION",
            memory_key=(
                "latest_job_recommendations"
            ),
            memory_value={
                "recommendations": (
                    stored_recommendations
                )
            },
            source="job_recommendation_agent",
            confidence_score=85,
        )

        return {
            "agent": (
                "job_recommendation_agent"
            ),
            "status": "COMPLETED",
            "run_id": str(run.id),
            "recommendations": (
                stored_recommendations
            ),
        }

    except Exception as exc:

        db.rollback()

        run.status = "FAILED"
        run.error_message = str(exc)
        run.completed_at = datetime.now(
            timezone.utc
        )

        db.add(run)
        db.commit()

        raise