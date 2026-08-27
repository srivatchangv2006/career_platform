from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.career_goal import CareerGoal
from models.career_recommendation import CareerRecommendation
from models.user import User
from schemas.career_goal import (
    CareerGoalCreate,
    CareerGoalResponse,
    CareerGoalUpdate,
    CareerRecommendationResponse,
)
from services.career_recommender import (
    generate_career_recommendations,
)
from services.memory_service import search_user_memories


router = APIRouter(
    prefix="/career-goals",
    tags=["Career Goals"],
)


@router.post(
    "",
    response_model=CareerGoalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_career_goal(
    goal_data: CareerGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = CareerGoal(
        user_id=current_user.id,
        **goal_data.model_dump(),
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    return goal


@router.get(
    "/me",
    response_model=list[CareerGoalResponse],
)
def get_my_career_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(CareerGoal)
        .filter(
            CareerGoal.user_id == current_user.id
        )
        .order_by(
            CareerGoal.is_active.desc(),
            CareerGoal.created_at.desc(),
        )
        .all()
    )


@router.get(
    "/{goal_id}",
    response_model=CareerGoalResponse,
)
def get_career_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = (
        db.query(CareerGoal)
        .filter(
            CareerGoal.id == goal_id,
            CareerGoal.user_id == current_user.id,
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found",
        )

    return goal


@router.put(
    "/{goal_id}",
    response_model=CareerGoalResponse,
)
def update_career_goal(
    goal_id: UUID,
    goal_data: CareerGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = (
        db.query(CareerGoal)
        .filter(
            CareerGoal.id == goal_id,
            CareerGoal.user_id == current_user.id,
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found",
        )

    update_data = goal_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(goal, field, value)

    goal.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(goal)

    return goal


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_career_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = (
        db.query(CareerGoal)
        .filter(
            CareerGoal.id == goal_id,
            CareerGoal.user_id == current_user.id,
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found",
        )

    db.delete(goal)
    db.commit()

    return None


@router.post(
    "/{goal_id}/recommendations",
    response_model=list[CareerRecommendationResponse],
    status_code=status.HTTP_201_CREATED,
)
def generate_career_goal_recommendations(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = (
        db.query(CareerGoal)
        .filter(
            CareerGoal.id == goal_id,
            CareerGoal.user_id == current_user.id,
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found",
        )

    memory_context = search_user_memories(
        db=db,
        user_id=current_user.id,
        query=(
            "candidate skills, experience, education, "
            "career preferences, skill gaps, job "
            "recommendations, career development, "
            "and feedback"
        ),
        limit=10,
    )

    candidate_context = {
        "user_id": str(current_user.id),
        "memory_context": memory_context,
    }

    goal_context = {
        "goal_title": goal.goal_title,
        "target_role": goal.target_role,
        "target_industry": goal.target_industry,
        "target_location": goal.target_location,
        "target_company": goal.target_company,
        "target_timeline": goal.target_timeline,
        "description": goal.description,
    }

    try:
        recommendations = (
            generate_career_recommendations(
                goal=goal_context,
                candidate_context=candidate_context,
            )
        )

        created = []

        for recommendation in recommendations:
            recommendation_record = CareerRecommendation(
                user_id=current_user.id,
                goal_id=goal.id,
                job_id=None,
                recommendation_type=(
                    recommendation[
                        "recommendation_type"
                    ]
                ),
                title=recommendation["title"],
                description=(
                    recommendation["description"]
                ),
                priority=recommendation["priority"],
                metadata={
                    "generated_by": "gemini-3.6-flash",
                    "source": "career_goal_agent",
                },
                is_completed=(
                    recommendation["is_completed"]
                ),
            )

            db.add(recommendation_record)
            created.append(
                recommendation_record
            )

        db.commit()

        for item in created:
            db.refresh(item)

        return created

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to generate career recommendations"
            ),
        ) from exc


@router.get(
    "/{goal_id}/recommendations",
    response_model=list[CareerRecommendationResponse],
)
def get_career_goal_recommendations(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = (
        db.query(CareerGoal)
        .filter(
            CareerGoal.id == goal_id,
            CareerGoal.user_id == current_user.id,
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found",
        )

    return (
        db.query(CareerRecommendation)
        .filter(
            CareerRecommendation.goal_id == goal_id,
            CareerRecommendation.user_id == current_user.id,
        )
        .order_by(
            CareerRecommendation.created_at.desc()
        )
        .all()
    )