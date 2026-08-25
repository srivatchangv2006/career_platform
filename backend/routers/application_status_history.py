from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.application import Application
from models.application_status_history import ApplicationStatusHistory
from models.user import User
from schemas.application_status_history import (
    ApplicationStatusHistoryCreate,
    ApplicationStatusHistoryResponse,
)

router = APIRouter(
    prefix="/applications",
    tags=["Application Status History"],
)


@router.post(
    "/{application_id}/status-history",
    response_model=ApplicationStatusHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_status_history(
    application_id: UUID,
    status_data: ApplicationStatusHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    history = ApplicationStatusHistory(
        application_id=application.id,
        status=status_data.status,
        changed_by=current_user.id,
        notes=status_data.notes,
    )

    db.add(history)

    # Keep the application's current status synchronized.
    application.status = status_data.status

    db.commit()
    db.refresh(history)

    return history


@router.get(
    "/{application_id}/status-history",
    response_model=list[ApplicationStatusHistoryResponse],
)
def get_status_history(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return (
        db.query(ApplicationStatusHistory)
        .filter(
            ApplicationStatusHistory.application_id == application_id
        )
        .order_by(ApplicationStatusHistory.created_at.asc())
        .all()
    )