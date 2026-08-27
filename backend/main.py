from fastapi import FastAPI
from routers.profiles import router as profiles_router
from routers.users import router as users_router
from routers.education import router as education_router
from routers.experience import router as experience_router
from routers.skills import router as skills_router
from routers.company import router as company_router
from routers.jobs import router as jobs_router
from routers.job_skills import router as job_skills_router
from routers.job_preferences import router as job_preferences_router
from routers.saved_jobs import router as saved_jobs_router
from routers.applications import router as applications_router
from routers.application_status_history import (
    router as application_status_history_router,
)
from routers.ai_interactions import (
    router as ai_interactions_router,
)
from routers.application_answers import (
    router as application_answers_router,
)
from routers.agent_memory import router as agent_memory_router
from routers.job_screening_questions import (
    router as job_screening_questions_router,
)
from routers.resumes import router as resumes_router
from routers.skill_gap_analysis import (
    router as skill_gap_analysis_router,
)
from routers.job_recommendations import (
    router as job_recommendations_router,
)
from routers.agent_tasks import router as agent_tasks_router
from routers.resume_analysis import router as resume_analysis_router
app = FastAPI(
    title="Career Platform API",
    description="Backend API for the Career Platform",
    version="1.0.0",
)
from routers.agent_task_steps import (
    router as agent_task_steps_router,
)
from routers.agent_feedback import (
    router as agent_feedback_router,
)
from routers.agent_messages import router as agent_messages_router
from routers.career_goals import router as career_goals_router
from routers.interview_preparation import (
    router as interview_preparation_router,
)
from routers.interviews import router as interviews_router
from routers.application_workspace import (
    router as application_workspace_router,
)
from routers.application_timeline import (
    router as application_timeline_router,
)
from routers.application_ai_activity import (
    router as application_ai_activity_router,
)
from routers.recruiter_applications import (
    router as recruiter_applications_router,
)
from routers.recruiter_interviews import (
    router as recruiter_interviews_router,
)
app.include_router(interview_preparation_router)
app.include_router(agent_feedback_router)
app.include_router(agent_task_steps_router)
app.include_router(agent_messages_router)
app.include_router(users_router)
app.include_router(recruiter_interviews_router)
app.include_router(recruiter_applications_router)
app.include_router(application_ai_activity_router)
app.include_router(application_timeline_router)
app.include_router(application_workspace_router)
app.include_router(interviews_router)
app.include_router(career_goals_router)
app.include_router(profiles_router)
app.include_router(education_router)
app.include_router(experience_router)
app.include_router(skills_router)
app.include_router(company_router)
app.include_router(jobs_router)
app.include_router(job_skills_router)
app.include_router(job_preferences_router)
app.include_router(saved_jobs_router)
app.include_router(applications_router)
app.include_router(application_status_history_router)
app.include_router(application_answers_router)
app.include_router(job_screening_questions_router)
app.include_router(resumes_router)
app.include_router(resume_analysis_router)
app.include_router(skill_gap_analysis_router)
app.include_router(job_recommendations_router)
app.include_router(agent_tasks_router)
app.include_router(agent_memory_router)
app.include_router(ai_interactions_router)

@app.get("/")
def root():
    return {
        "message": "Career Platform API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }