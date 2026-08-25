from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.education import Education
from models.user import User
from schemas.education import (
    EducationCreate,
    EducationResponse,
    EducationUpdate,
)


router = APIRouter(
    prefix="/education",
    tags=["Education"],
)


@router.post(
    "",
    response_model=EducationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_education(
    education_data: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    education = Education(
        user_id=current_user.id,
        **education_data.model_dump(),
    )

    db.add(education)
    db.commit()
    db.refresh(education)

    return education


@router.get(
    "",
    response_model=list[EducationResponse],
)
def get_my_education(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    education_records = (
        db.query(Education)
        .filter(Education.user_id == current_user.id)
        .order_by(Education.start_date.desc())
        .all()
    )

    return education_records


@router.put(
    "/{education_id}",
    response_model=EducationResponse,
)
def update_education(
    education_id: UUID,
    education_data: EducationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    education = (
        db.query(Education)
        .filter(
            Education.id == education_id,
            Education.user_id == current_user.id,
        )
        .first()
    )

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education record not found",
        )

    update_data = education_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(education, field, value)

    db.commit()
    db.refresh(education)

    return education


@router.delete(
    "/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_education(
    education_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    education = (
        db.query(Education)
        .filter(
            Education.id == education_id,
            Education.user_id == current_user.id,
        )
        .first()
    )

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education record not found",
        )

    db.delete(education)
    db.commit()

    return None