from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role

from models.skill import Skill
from models.user import User
from models.user_skill import UserSkill

from schemas.skill import (
    SkillCreate,
    SkillResponse,
    UserSkillCreate,
    UserSkillResponse,
    UserSkillUpdate,
)


router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
    dependencies=[Depends(get_current_user)],
)


# ==================================================
# Global Skills
# ==================================================

@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("CANDIDATE"))],
)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    existing_skill = (
        db.query(Skill)
        .filter(
            Skill.slug == skill_data.slug
        )
        .first()
    )

    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill already exists",
        )

    skill = Skill(
        **skill_data.model_dump()
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


@router.get(
    "",
    response_model=list[SkillResponse],
)
def get_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        db.query(Skill)
        .order_by(
            Skill.name.asc()
        )
        .all()
    )


# ==================================================
# Candidate-owned User Skills
# ==================================================

@router.post(
    "/me",
    response_model=UserSkillResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("CANDIDATE"))],
)
def add_my_skill(
    skill_data: UserSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
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

    existing_user_skill = (
        db.query(UserSkill)
        .filter(
            UserSkill.user_id
            == current_user.id,
            UserSkill.skill_id
            == skill_data.skill_id,
        )
        .first()
    )

    if existing_user_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill already added to your profile",
        )

    user_skill = UserSkill(
        user_id=current_user.id,
        **skill_data.model_dump(),
    )

    db.add(user_skill)
    db.commit()
    db.refresh(user_skill)

    return user_skill


@router.get(
    "/me",
    response_model=list[UserSkillResponse],
    dependencies=[Depends(require_role("CANDIDATE"))],
)
def get_my_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    return (
        db.query(UserSkill)
        .filter(
            UserSkill.user_id
            == current_user.id
        )
        .order_by(
            UserSkill.created_at.desc()
        )
        .all()
    )


@router.put(
    "/me/{skill_id}",
    response_model=UserSkillResponse,
    dependencies=[Depends(require_role("CANDIDATE"))],
)
def update_my_skill(
    skill_id: UUID,
    skill_data: UserSkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    user_skill = (
        db.query(UserSkill)
        .filter(
            UserSkill.user_id
            == current_user.id,
            UserSkill.skill_id
            == skill_id,
        )
        .first()
    )

    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found in your profile",
        )

    update_data = skill_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            user_skill,
            field,
            value,
        )

    db.commit()
    db.refresh(user_skill)

    return user_skill


@router.delete(
    "/me/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("CANDIDATE"))],
)
def delete_my_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    user_skill = (
        db.query(UserSkill)
        .filter(
            UserSkill.user_id
            == current_user.id,
            UserSkill.skill_id
            == skill_id,
        )
        .first()
    )

    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found in your profile",
        )

    db.delete(user_skill)
    db.commit()

    return None