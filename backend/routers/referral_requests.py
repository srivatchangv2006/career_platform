from datetime import datetime, timezone
from uuid import UUID

from io import BytesIO

from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.resume import Resume
from services.azure_blob_download import download_blob
from models.referral import (
    Referral,
    ReferralOpportunity,
    ReferralOpportunityStatus,
    ReferralStatus,
)
from models.profile import Profile
from models.user import User

from schemas.referral import (
    ReferralRequestCreate,
    ReferralRequestUpdate,
    ReferralResponse,
)


router = APIRouter(
    prefix="/referral-requests",
    tags=["Referral Requests"],
)


def build_referral_response(
    db: Session,
    referral: Referral,
):
    requester = (
        db.query(User)
        .filter(
            User.id
            == referral.requester_id
        )
        .first()
    )

    resume = None

    if referral.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id
                == referral.resume_id
            )
            .first()
        )

    requester_name = (
        requester.email
        if requester
        else "User"
    )

    if requester:
        profile = (
            db.query(Profile)
            .filter(
                Profile.user_id
                == requester.id
            )
            .first()
        )

        if profile and profile.full_name:
            requester_name = (
                profile.full_name
            )

    return ReferralResponse(
        id=referral.id,
        opportunity_id=(
            referral.opportunity_id
        ),
        requester_id=(
            referral.requester_id
        ),
        requester_name=requester_name,
        resume_id=referral.resume_id,
        resume_name=(
            resume.file_name
            if resume
            else None
        ),
        message=referral.message,
        status=referral.status,
        created_at=referral.created_at,
        updated_at=referral.updated_at,
    )



@router.post(
    "/for/{opportunity_id}",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_referral_request(
    opportunity_id: UUID,
    request_data: ReferralRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opportunity = (
        db.query(ReferralOpportunity)
        .filter(
            ReferralOpportunity.id == opportunity_id
        )
        .first()
    )

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral opportunity not found",
        )

    if opportunity.status != ReferralOpportunityStatus.OPEN.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This referral opportunity is closed",
        )

    if opportunity.posted_by == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot request your own referral opportunity",
        )

    if request_data.resume_id is not None:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id == request_data.resume_id,
                Resume.user_id == current_user.id,
            )
            .first()
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

    existing_request = (
        db.query(Referral)
        .filter(
            Referral.opportunity_id == opportunity.id,
            Referral.requester_id == current_user.id,
            Referral.status.in_(
                [
                    ReferralStatus.PENDING,
                    ReferralStatus.ACCEPTED,
                ]
            ),
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "You already have an active referral request "
                "for this opportunity"
            ),
        )

    referral = Referral(
        opportunity_id=opportunity.id,
        requester_id=current_user.id,
        resume_id=request_data.resume_id,
        message=request_data.message,
        status=ReferralStatus.PENDING,
    )

    db.add(referral)
    db.commit()
    db.refresh(referral)

    return build_referral_response(
        db,
        referral,
    )


@router.get(
    "/sent",
    response_model=list[ReferralResponse],
)
def get_sent_referral_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    referrals = (
        db.query(Referral)
        .filter(
            Referral.requester_id
            == current_user.id
        )
        .order_by(
            Referral.created_at.desc()
        )
        .all()
    )

    return [
        build_referral_response(
            db,
            referral,
        )
        for referral in referrals
    ]


@router.get(
    "/received",
    response_model=list[ReferralResponse],
)
def get_received_referral_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    referrals = (
        db.query(Referral)
        .join(
            ReferralOpportunity,
            ReferralOpportunity.id
            == Referral.opportunity_id,
        )
        .filter(
            ReferralOpportunity.posted_by
            == current_user.id
        )
        .order_by(
            Referral.created_at.desc()
        )
        .all()
    )

    return [
        build_referral_response(
            db,
            referral,
        )
        for referral in referrals
    ]


@router.get(
    "/{referral_id}",
    response_model=ReferralResponse,
)
def get_referral_request(
    referral_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    referral = (
        db.query(Referral)
        .join(
            ReferralOpportunity,
            ReferralOpportunity.id
            == Referral.opportunity_id,
        )
        .filter(
            Referral.id == referral_id,
        )
        .first()
    )

    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral request not found",
        )

    if (
        referral.requester_id != current_user.id
        and (
            opportunity_owned_by_user(
                db,
                referral.opportunity_id,
                current_user.id,
            )
            is False
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this referral request",
        )

    return build_referral_response(
        db,
        referral,
    )


@router.put(
    "/{referral_id}",
    response_model=ReferralResponse,
)
def update_referral_request(
    referral_id: UUID,
    request_data: ReferralRequestUpdate,
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
            detail="Referral request not found",
        )

    opportunity = (
        db.query(ReferralOpportunity)
        .filter(
            ReferralOpportunity.id
            == referral.opportunity_id
        )
        .first()
    )

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral opportunity not found",
        )

    if referral.status != ReferralStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending referral requests can be updated",
        )

    requested_status = request_data.status.upper()

    if referral.requester_id == current_user.id:

        if requested_status != "CANCELLED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requester can only cancel a pending request",
            )

        referral.status = ReferralStatus.CANCELLED

    elif opportunity.posted_by == current_user.id:

        if requested_status not in {
            "ACCEPTED",
            "REJECTED",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Opportunity owner can only "
                    "accept or reject requests"
                ),
            )

        if requested_status == "ACCEPTED":

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

            if (
                opportunity.max_referrals is not None
                and accepted_count
                >= opportunity.max_referrals
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Maximum accepted referrals "
                        "for this opportunity has been reached"
                    ),
                )

            referral.status = ReferralStatus.ACCEPTED

            if (
                opportunity.max_referrals is not None
                and (
                    accepted_count + 1
                    >= opportunity.max_referrals
                )
            ):
                opportunity.status = (
                    ReferralOpportunityStatus.CLOSED.value
                )
                opportunity.updated_at = datetime.now(
                    timezone.utc
                )

        else:
            referral.status = ReferralStatus.REJECTED

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this referral request",
        )

    referral.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(referral)

    return build_referral_response(
        db,
        referral,
    )


@router.delete(
    "/{referral_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_referral_request(
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
            detail="Referral request not found",
        )

    if referral.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester can cancel this request",
        )

    if referral.status != ReferralStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending requests can be deleted",
        )

    referral.status = ReferralStatus.CANCELLED
    referral.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()

    return None


def opportunity_owned_by_user(
    db: Session,
    opportunity_id: UUID,
    user_id: UUID,
) -> bool:
    return (
        db.query(ReferralOpportunity)
        .filter(
            ReferralOpportunity.id == opportunity_id,
            ReferralOpportunity.posted_by == user_id,
        )
        .first()
        is not None
    )


# ============================================================
# VIEW / DOWNLOAD REFERRAL RESUME
#
# Only the owner of the referral opportunity can access the
# candidate's attached resume.
# ============================================================

@router.get(
    "/{referral_id}/resume",
)
def download_referral_resume(
    referral_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    referral = (
        db.query(Referral)
        .join(
            ReferralOpportunity,
            ReferralOpportunity.id
            == Referral.opportunity_id,
        )
        .filter(
            Referral.id == referral_id,
            ReferralOpportunity.posted_by
            == current_user.id,
        )
        .first()
    )

    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral request not found",
        )

    if not referral.resume_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume attached to this referral request",
        )

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == referral.resume_id,
            Resume.user_id == referral.requester_id,
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    try:
        file_bytes = download_blob(
            container_name=resume.blob_container,
            blob_path=resume.blob_path,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to download resume",
        ) from exc

    return StreamingResponse(
        BytesIO(file_bytes),
        media_type=(
            resume.content_type
            or "application/pdf"
        ),
        headers={
            "Content-Disposition": (
                f'inline; filename="{resume.file_name}"'
            ),
        },
    )
