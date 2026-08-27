import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    AdviceRequest,
    AgentFeedback,
    AgentMemory,
    AgentMemoryEmbedding,
    AgentMessage,
    AgentTask,
    AgentTaskStep,
    AIInteraction,
    Application,
    ApplicationAnswer,
    ApplicationStatusHistory,
    CareerGoal,
    CareerRecommendation,
    CommunityComment,
    CommunityPost,
    CommunityVote,
    Company,
    Connection,
    Education,
    Experience,
    Interview,
    InterviewPreparation,
    Job,
    JobMatch,
    JobPreference,
    JobRecommendationItem,
    JobRecommendationRun,
    JobReport,
    JobScreeningQuestion,
    JobSkill,
    Notification,
    Profile,
    ProfileView,
    RecruiterProfile,
    Referral,
    Resume,
    ResumeAnalysis,
    SavedJob,
    Skill,
    SkillGapAnalysis,
    User,
    UserActivity,
    UserFollow,
    UserSkill,
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set"
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)