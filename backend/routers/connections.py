from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.connections import (
    Connection,
    ConnectionStatus,
)
from models.user import User

from schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate,
)

from services.public_user import (
    get_public_user,
)


router = APIRouter(
    prefix="/connections",
    tags=["Connections"],
)


def build_connection_response(
    db: Session,
    connection: Connection,
) -> ConnectionResponse:
    connection_status = (
        connection.status.value
        if hasattr(
            connection.status,
            "value",
        )
        else str(connection.status)
    )

    return ConnectionResponse(
        id=connection.id,
        requester_id=connection.requester_id,
        receiver_id=connection.receiver_id,
        status=connection_status,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
        requester=get_public_user(
            db,
            connection.requester_id,
        ),
        receiver=get_public_user(
            db,
            connection.receiver_id,
        ),
    )


def user_matches_search(
    user_data,
    search: str | None,
) -> bool:
    if not search:
        return True

    search_value = (
        search.strip().lower()
    )

    searchable = " ".join(
        [
            user_data["display_name"],
            user_data["handle"],
            user_data["role"],
            user_data["headline"] or "",
            user_data["location"] or "",
            user_data["company_name"] or "",
        ]
    ).lower()

    return search_value in searchable


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
    receiver_id = (
        connection_data.receiver_id
    )

    if receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "You cannot send a connection "
                "request to yourself"
            ),
        )

    receiver = (
        db.query(User)
        .filter(
            User.id == receiver_id,
        )
        .first()
    )

    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing = (
        db.query(Connection)
        .filter(
            or_(
                (
                    Connection.requester_id
                    == current_user.id
                )
                & (
                    Connection.receiver_id
                    == receiver_id
                ),
                (
                    Connection.requester_id
                    == receiver_id
                )
                & (
                    Connection.receiver_id
                    == current_user.id
                ),
            )
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A connection already exists "
                "between these users"
            ),
        )

    connection = Connection(
        requester_id=current_user.id,
        receiver_id=receiver_id,
        status=ConnectionStatus.PENDING,
    )

    db.add(connection)
    db.commit()
    db.refresh(connection)

    return build_connection_response(
        db,
        connection,
    )


@router.get(
    "/me",
    response_model=list[ConnectionResponse],
)
def get_my_connections(
    q: str | None = Query(
        default=None,
        min_length=2,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connections = (
        db.query(Connection)
        .filter(
            or_(
                Connection.requester_id
                == current_user.id,
                Connection.receiver_id
                == current_user.id,
            ),
            Connection.status
            == ConnectionStatus.ACCEPTED,
        )
        .order_by(
            Connection.updated_at.desc()
        )
        .all()
    )

    results = []

    for connection in connections:
        requester = get_public_user(
            db,
            connection.requester_id,
        )

        receiver = get_public_user(
            db,
            connection.receiver_id,
        )

        other_user = (
            receiver
            if connection.requester_id
            == current_user.id
            else requester
        )

        if not other_user:
            continue

        if not user_matches_search(
            other_user,
            q,
        ):
            continue

        results.append(
            ConnectionResponse(
                id=connection.id,
                requester_id=(
                    connection.requester_id
                ),
                receiver_id=(
                    connection.receiver_id
                ),
                status="ACCEPTED",
                created_at=(
                    connection.created_at
                ),
                updated_at=(
                    connection.updated_at
                ),
                requester=requester,
                receiver=receiver,
            )
        )

    return results


@router.get(
    "/requests",
    response_model=list[ConnectionResponse],
)
def get_connection_requests(
    q: str | None = Query(
        default=None,
        min_length=2,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requests = (
        db.query(Connection)
        .filter(
            Connection.receiver_id
            == current_user.id,
            Connection.status
            == ConnectionStatus.PENDING,
        )
        .order_by(
            Connection.created_at.desc()
        )
        .all()
    )

    results = []

    for connection in requests:
        requester = get_public_user(
            db,
            connection.requester_id,
        )

        receiver = get_public_user(
            db,
            connection.receiver_id,
        )

        if not requester:
            continue

        if not user_matches_search(
            requester,
            q,
        ):
            continue

        results.append(
            ConnectionResponse(
                id=connection.id,
                requester_id=(
                    connection.requester_id
                ),
                receiver_id=(
                    connection.receiver_id
                ),
                status="PENDING",
                created_at=(
                    connection.created_at
                ),
                updated_at=(
                    connection.updated_at
                ),
                requester=requester,
                receiver=receiver,
            )
        )

    return results


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
            Connection.id == connection_id,
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    if (
        connection.receiver_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the receiver can update "
                "this connection request"
            ),
        )

    if (
        connection.status
        != ConnectionStatus.PENDING
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only pending connection requests "
                "can be updated"
            ),
        )

    requested_status = (
        connection_data.status.upper()
    )

    if requested_status not in {
        "ACCEPTED",
        "REJECTED",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid connection status. "
                "Allowed values: ACCEPTED, REJECTED"
            ),
        )

    connection.status = (
        ConnectionStatus(
            requested_status
        )
    )

    connection.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(connection)

    return build_connection_response(
        db,
        connection,
    )


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
            Connection.id == connection_id,
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    if (
        connection.requester_id
        != current_user.id
        and connection.receiver_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not part of this connection"
            ),
        )

    db.delete(connection)
    db.commit()

    return None
