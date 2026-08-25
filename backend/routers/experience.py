from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.experience import Experience
from models.user import User
from schemas.experience import (
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
)


router = APIRouter(
    prefix="/experience",
    tags=["Experience"],
)


@router.post(
    "",
    response_model=ExperienceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_experience(
    experience_data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experience = Experience(
        user_id=current_user.id,
        **experience_data.model_dump(),
    )

    db.add(experience)
    db.commit()
    db.refresh(experience)

    return experience


@router.get(
    "",
    response_model=list[ExperienceResponse],
)
def get_my_experience(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experience_records = (
        db.query(Experience)
        .filter(Experience.user_id == current_user.id)
        .order_by(Experience.start_date.desc())
        .all()
    )

    return experience_records


@router.put(
    "/{experience_id}",
    response_model=ExperienceResponse,
)
def update_experience(
    experience_id: UUID,
    experience_data: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experience = (
        db.query(Experience)
        .filter(
            Experience.id == experience_id,
            Experience.user_id == current_user.id,
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience record not found",
        )

    update_data = experience_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(experience, field, value)

    db.commit()
    db.refresh(experience)

    return experience


@router.delete(
    "/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_experience(
    experience_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experience = (
        db.query(Experience)
        .filter(
            Experience.id == experience_id,
            Experience.user_id == current_user.id,
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience record not found",
        )

    db.delete(experience)
    db.commit()

    return None