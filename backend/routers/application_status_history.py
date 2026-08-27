from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.application import Application
from models.application_status_history import (
    ApplicationStatusHistory,
)
from models.user import User

from schemas.application_status_history import (
    ApplicationStatusHistoryCreate,
    ApplicationStatusHistoryResponse,
)


router = APIRouter(
    prefix="/applications",
    tags=["Application Status History"],
    dependencies=[
        Depends(require_role("CANDIDATE"))
    ],
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
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    # --------------------------------------------------------
    # Candidate can only modify their own application.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Candidate-controlled status transitions.
    #
    # Candidates are allowed to withdraw their own
    # application. Recruiter-controlled hiring statuses
    # must be changed through:
    #
    # PUT /recruiter/applications/{application_id}/status
    # --------------------------------------------------------

    current_status = (
        application.status.value
        if hasattr(application.status, "value")
        else str(application.status)
    )

    requested_status = (
        status_data.status.value
        if hasattr(status_data.status, "value")
        else str(status_data.status)
    )

    if requested_status != "WITHDRAWN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only withdraw their "
                "own applications. Recruiter-controlled "
                "application statuses must be updated "
                "through the recruiter application workflow."
            ),
        )

    # --------------------------------------------------------
    # Withdrawal should not be repeated.
    # --------------------------------------------------------

    if current_status == "WITHDRAWN":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application is already withdrawn",
        )

    # --------------------------------------------------------
    # Prevent withdrawal after terminal recruiter status.
    # --------------------------------------------------------

    terminal_statuses = {
        "OFFER",
        "REJECTED",
    }

    if current_status in terminal_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Application cannot be withdrawn after "
                f"status {current_status}"
            ),
        )

    # --------------------------------------------------------
    # Create history record.
    # --------------------------------------------------------

    history = ApplicationStatusHistory(
        application_id=application.id,
        status=status_data.status,
        changed_by=current_user.id,
        notes=status_data.notes,
    )

    db.add(history)

    # Keep current application status synchronized.
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
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
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
            ApplicationStatusHistory.application_id
            == application_id
        )
        .order_by(
            ApplicationStatusHistory.created_at.asc()
        )
        .all()
    )