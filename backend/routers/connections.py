from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from dependencies import get_db
from dependencies.auth import get_current_user
from models.connections import Connection, ConnectionStatus
from models.connections import Connection
from models.user import User

from schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate,
)


router = APIRouter(
    prefix="/connections",
    tags=["Connections"],
)


ALLOWED_UPDATE_STATUSES = {
    "ACCEPTED",
    "REJECTED",
}


# ============================================================
# CREATE CONNECTION REQUEST
# ============================================================

@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_connection(
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receiver_id = connection_data.receiver_id

    # --------------------------------------------------------
    # Cannot connect to yourself.
    # --------------------------------------------------------

    if receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send a connection request to yourself",
        )

    # --------------------------------------------------------
    # Receiver must exist.
    # --------------------------------------------------------

    receiver = (
        db.query(User)
        .filter(
            User.id == receiver_id
        )
        .first()
    )

    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # --------------------------------------------------------
    # Prevent duplicate connection in either direction.
    # --------------------------------------------------------

    existing = (
        db.query(Connection)
        .filter(
            or_(
                (
                    (Connection.requester_id == current_user.id)
                    & (Connection.receiver_id == receiver_id)
                ),
                (
                    (Connection.requester_id == receiver_id)
                    & (Connection.receiver_id == current_user.id)
                ),
            )
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A connection already exists between these users",
        )

    # --------------------------------------------------------
    # Create pending request.
    # --------------------------------------------------------

    connection = Connection(
        requester_id=current_user.id,
        receiver_id=receiver_id,
        status=ConnectionStatus.PENDING,
    )

    db.add(connection)
    db.commit()
    db.refresh(connection)

    return connection


# ============================================================
# GET MY CONNECTIONS
# ============================================================

@router.get(
    "/me",
    response_model=list[ConnectionResponse],
)
def get_my_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Connection)
        .filter(
            or_(
                Connection.requester_id == current_user.id,
                Connection.receiver_id == current_user.id,
            )
        )
        .order_by(
            Connection.updated_at.desc()
        )
        .all()
    )


# ============================================================
# GET INCOMING CONNECTION REQUESTS
# ============================================================

@router.get(
    "/requests",
    response_model=list[ConnectionResponse],
)
def get_connection_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Connection)
        .filter(
            Connection.receiver_id == current_user.id,
            Connection.status == ConnectionStatus.PENDING
        )
        .order_by(
            Connection.created_at.desc()
        )
        .all()
    )


# ============================================================
# ACCEPT / REJECT CONNECTION REQUEST
#
# Only the RECEIVER can accept/reject.
# ============================================================

@router.put(
    "/{connection_id}",
    response_model=ConnectionResponse,
)
def update_connection(
    connection_id: UUID,
    connection_data: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = (
        db.query(Connection)
        .filter(
            Connection.id == connection_id
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # --------------------------------------------------------
    # Only receiver may accept/reject.
    # --------------------------------------------------------

    if connection.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the receiver can update this connection request",
        )

    if connection.status != ConnectionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending connection requests can be updated",
        )

    requested_status = connection_data.status.upper()

    if requested_status not in ALLOWED_UPDATE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid connection status. "
                "Allowed values: ACCEPTED, REJECTED"
            ),
        )

    connection.status = ConnectionStatus(requested_status)
    connection.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(connection)

    return connection


# ============================================================
# DELETE CONNECTION
#
# Either participant may remove an existing connection.
# Requester may also cancel a pending request.
# ============================================================

@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_connection(
    connection_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = (
        db.query(Connection)
        .filter(
            Connection.id == connection_id
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    if (
        connection.requester_id != current_user.id
        and connection.receiver_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this connection",
        )

    db.delete(connection)
    db.commit()

    return None
