from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.job import Job
from models.referral import (
    Referral,
    ReferralOpportunity,
    ReferralOpportunityStatus,
    ReferralStatus,
)
from models.user import User

from schemas.referral_opportunity import (
    ReferralOpportunityCreate,
    ReferralOpportunityResponse,
    ReferralOpportunityUpdate,
)


router = APIRouter(
    prefix="/referral-opportunities",
    tags=["Referral Opportunities"],
)


# ============================================================
# HELPER
# Build a complete opportunity response including:
#   - accepted_referrals
#   - remaining_referrals
# ============================================================

def build_opportunity_response(
    db: Session,
    opportunity: ReferralOpportunity,
) -> ReferralOpportunityResponse:
    accepted_count = (
        db.query(Referral)
        .filter(
            Referral.opportunity_id == opportunity.id,
            Referral.status == ReferralStatus.ACCEPTED,
        )
        .count()
    )

    remaining_count = (
        None
        if opportunity.max_referrals is None
        else max(
            opportunity.max_referrals - accepted_count,
            0,
        )
    )

    return ReferralOpportunityResponse(
        id=opportunity.id,
        posted_by=opportunity.posted_by,
        job_id=opportunity.job_id,
        message=opportunity.message,
        max_referrals=opportunity.max_referrals,
        accepted_referrals=accepted_count,
        remaining_referrals=remaining_count,
        status=opportunity.status,
        created_at=opportunity.created_at,
        updated_at=opportunity.updated_at,
    )


# ============================================================
# CREATE REFERRAL OPPORTUNITY
#
# Any authenticated user may offer referrals.
# ============================================================

@router.post(
    "",
    response_model=ReferralOpportunityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_referral_opportunity(
    opportunity_data: ReferralOpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Validate job.
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == opportunity_data.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # --------------------------------------------------------
    # Validate max_referrals.
    #
    # NULL = unlimited referral capacity.
    # --------------------------------------------------------

    if (
        opportunity_data.max_referrals is not None
        and opportunity_data.max_referrals <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="max_referrals must be greater than 0",
        )

    # --------------------------------------------------------
    # Create opportunity.
    # --------------------------------------------------------

    opportunity = ReferralOpportunity(
        posted_by=current_user.id,
        job_id=opportunity_data.job_id,
        message=opportunity_data.message,
        max_referrals=opportunity_data.max_referrals,
        status=ReferralOpportunityStatus.OPEN.value,
    )

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    return build_opportunity_response(
        db,
        opportunity,
    )


# ============================================================
# GET OPEN REFERRAL OPPORTUNITIES
#
# Available to any authenticated user.
# ============================================================

@router.get(
    "",
    response_model=list[ReferralOpportunityResponse],
)
def get_referral_opportunities(
    job_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(ReferralOpportunity)
        .filter(
            ReferralOpportunity.status
            == ReferralOpportunityStatus.OPEN.value
        )
    )

    if job_id is not None:
        query = query.filter(
            ReferralOpportunity.job_id == job_id
        )

    opportunities = (
        query
        .order_by(
            ReferralOpportunity.created_at.desc()
        )
        .all()
    )

    return [
        build_opportunity_response(
            db,
            opportunity,
        )
        for opportunity in opportunities
    ]


# ============================================================
# GET ONE REFERRAL OPPORTUNITY
# ============================================================

@router.get(
    "/{opportunity_id}",
    response_model=ReferralOpportunityResponse,
)
def get_referral_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opportunity = (
        db.query(ReferralOpportunity)
        .filter(
            ReferralOpportunity.id
            == opportunity_id
        )
        .first()
    )

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral opportunity not found",
        )

    return build_opportunity_response(
        db,
        opportunity,
    )


# ============================================================
# UPDATE REFERRAL OPPORTUNITY
#
# Only the user who posted the opportunity can update it.
# ============================================================

@router.put(
    "/{opportunity_id}",
    response_model=ReferralOpportunityResponse,
)
def update_referral_opportunity(
    opportunity_id: UUID,
    opportunity_data: ReferralOpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opportunity = (
        db.query(ReferralOpportunity)
        .filter(
            ReferralOpportunity.id
            == opportunity_id
        )
        .first()
    )

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral opportunity not found",
        )

    # --------------------------------------------------------
    # Only owner can update.
    # --------------------------------------------------------

    if opportunity.posted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the opportunity owner can update it",
        )

    update_data = opportunity_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # Validate max_referrals.
    # --------------------------------------------------------

    if (
        "max_referrals" in update_data
        and update_data["max_referrals"] is not None
        and update_data["max_referrals"] <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="max_referrals must be greater than 0",
        )

    # --------------------------------------------------------
    # Count accepted referrals.
    # --------------------------------------------------------

    accepted_count = (
        db.query(Referral)
        .filter(
            Referral.opportunity_id
            == opportunity.id,
            Referral.status
            == ReferralStatus.ACCEPTED,
        )
        .count()
    )

    # --------------------------------------------------------
    # Prevent capacity from being reduced below the number
    # of already accepted referrals.
    #
    # Example:
    #   current accepted = 3
    #   new max_referrals = 2
    #   => reject
    #
    # NULL means unlimited and is allowed.
    # --------------------------------------------------------

    if (
        "max_referrals" in update_data
        and update_data["max_referrals"] is not None
        and update_data["max_referrals"]
        < accepted_count
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "max_referrals cannot be less than "
                "the number of accepted referrals"
            ),
        )

    # --------------------------------------------------------
    # Validate opportunity status.
    # --------------------------------------------------------

    if "status" in update_data:
        requested_status = (
            update_data["status"].upper()
        )

        if requested_status not in {
            "OPEN",
            "CLOSED",
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be OPEN or CLOSED",
            )

        # If trying to OPEN an opportunity whose capacity is
        # already full, reject it.
        effective_capacity = update_data.get(
            "max_referrals",
            opportunity.max_referrals,
        )

        if (
            requested_status == "OPEN"
            and effective_capacity is not None
            and accepted_count >= effective_capacity
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Opportunity cannot be opened because "
                    "maximum referral capacity has already "
                    "been reached"
                ),
            )

        update_data["status"] = requested_status

    # --------------------------------------------------------
    # Apply updates.
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            opportunity,
            field,
            value,
        )

    opportunity.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(opportunity)

    return build_opportunity_response(
        db,
        opportunity,
    )


# ============================================================
# DELETE REFERRAL OPPORTUNITY
#
# Only the owner can delete it.
#
# Because referrals have ON DELETE CASCADE for
# opportunity_id, deleting the opportunity also removes
# its referral requests.
# ============================================================

@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_referral_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opportunity = (
        db.query(ReferralOpportunity)
        .filter(
            ReferralOpportunity.id
            == opportunity_id
        )
        .first()
    )

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral opportunity not found",
        )

    if opportunity.posted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the opportunity owner can delete it",
        )

    db.delete(opportunity)
    db.commit()

    return None