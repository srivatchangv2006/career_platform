from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.connections import Connection, ConnectionStatus
from models.job import Job
from models.referral import Referral, ReferralStatus
from models.user import User

from schemas.referral import (
    ReferralCreate,
    ReferralResponse,
    ReferralUpdate,
)


router = APIRouter(
    prefix="/referrals",
    tags=["Referrals"],
)


# ============================================================
# CREATE REFERRAL REQUEST
#
# Any authenticated user may request a referral.
#
# Rules:
#   - requester != referrer
#   - requester must exist (current user)
#   - referrer must exist
#   - job must exist
#   - requester cannot submit duplicate active referrals
# ============================================================

@router.post(
    "",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_referral(
    referral_data: ReferralCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if referral_data.referrer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot request a referral from yourself",
        )

    referrer = (
        db.query(User)
        .filter(
            User.id == referral_data.referrer_id
        )
        .first()
    )

    if not referrer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referrer not found",
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == referral_data.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # --------------------------------------------------------
    # Prevent duplicate active referral requests for the same
    # requester/referrer/job combination.
    # --------------------------------------------------------

    existing_referral = (
        db.query(Referral)
        .filter(
            Referral.requester_id == current_user.id,
            Referral.referrer_id == referral_data.referrer_id,
            Referral.job_id == referral_data.job_id,
            Referral.status.in_(
                [
                    ReferralStatus.PENDING,
                    ReferralStatus.ACCEPTED,
                ]
            ),
        )
        .first()
    )

    if existing_referral:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An active referral already exists "
                "for this user and job"
            ),
        )

    referral = Referral(
        requester_id=current_user.id,
        referrer_id=referral_data.referrer_id,
        job_id=referral_data.job_id,
        message=referral_data.message,
        status=ReferralStatus.PENDING,
    )

    db.add(referral)
    db.commit()
    db.refresh(referral)

    return referral


# ============================================================
# GET SENT REFERRALS
# ============================================================

@router.get(
    "/sent",
    response_model=list[ReferralResponse],
)
def get_sent_referrals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Referral)
        .filter(
            Referral.requester_id == current_user.id
        )
        .order_by(
            Referral.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET RECEIVED REFERRALS
# ============================================================

@router.get(
    "/received",
    response_model=list[ReferralResponse],
)
def get_received_referrals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Referral)
        .filter(
            Referral.referrer_id == current_user.id
        )
        .order_by(
            Referral.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET ONE REFERRAL
#
# Only requester or referrer can view it.
# ============================================================

@router.get(
    "/{referral_id}",
    response_model=ReferralResponse,
)
def get_referral(
    referral_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    referral = (
        db.query(Referral)
        .filter(
            Referral.id == referral_id,
            or_(
                Referral.requester_id
                == current_user.id,
                Referral.referrer_id
                == current_user.id,
            ),
        )
        .first()
    )

    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found",
        )

    return referral


# ============================================================
# UPDATE REFERRAL
#
# REQUESTER:
#   PENDING -> CANCELLED
#
# REFERRER:
#   PENDING -> ACCEPTED
#   PENDING -> REJECTED
# ============================================================

@router.put(
    "/{referral_id}",
    response_model=ReferralResponse,
)
def update_referral(
    referral_id: UUID,
    referral_data: ReferralUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    referral = (
        db.query(Referral)
        .filter(
            Referral.id == referral_id
        )
        .first()
    )

    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found",
        )

    requested_status = referral_data.status.upper()

    if referral.status != ReferralStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending referrals can be updated",
        )

    # --------------------------------------------------------
    # Requester can cancel.
    # --------------------------------------------------------

    if (
        referral.requester_id == current_user.id
    ):
        if requested_status != "CANCELLED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "The requester can only cancel "
                    "a pending referral"
                ),
            )

        referral.status = ReferralStatus.CANCELLED

    # --------------------------------------------------------
    # Referrer can accept/reject.
    # --------------------------------------------------------

    elif (
        referral.referrer_id == current_user.id
    ):
        if requested_status not in {
            "ACCEPTED",
            "REJECTED",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "The referrer can only "
                    "accept or reject a referral"
                ),
            )

        referral.status = ReferralStatus(
            requested_status
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this referral",
        )

    referral.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(referral)

    return referral


# ============================================================
# DELETE REFERRAL
#
# Only requester can delete/cancel their own referral.
# ============================================================

@router.delete(
    "/{referral_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_referral(
    referral_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    referral = (
        db.query(Referral)
        .filter(
            Referral.id == referral_id
        )
        .first()
    )

    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found",
        )

    if referral.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester can delete a referral",
        )

    if referral.status != ReferralStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending referrals can be deleted",
        )

    db.delete(referral)
    db.commit()

    return None
