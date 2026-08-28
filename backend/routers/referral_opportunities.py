from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.company import Company
from models.job import Job
from models.profile import Profile
from models.referral import (
    Referral,
    ReferralOpportunity,
    ReferralOpportunityStatus,
    ReferralStatus,
)
from models.recruiter_profile import RecruiterProfile
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


def get_display_user(
    db: Session,
    user: User,
):
    role = (
        user.role.value
        if hasattr(user.role, "value")
        else str(user.role)
    )

    profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == user.id
        )
        .first()
    )

    if profile and profile.full_name:
        return profile.full_name, role

    recruiter_profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id
            == user.id
        )
        .first()
    )

    if recruiter_profile:
        return user.email, role

    return user.email, role


def build_opportunity_response(
    db: Session,
    opportunity: ReferralOpportunity,
) -> ReferralOpportunityResponse:
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

    remaining_count = (
        None
        if opportunity.max_referrals is None
        else max(
            opportunity.max_referrals
            - accepted_count,
            0,
        )
    )

    job = None

    if opportunity.job_id is not None:
        job = (
            db.query(Job)
            .filter(
                Job.id
                == opportunity.job_id
            )
            .first()
        )

    if job:
        company = (
            db.query(Company)
            .filter(
                Company.id
                == job.company_id
            )
            .first()
        )

        job_title = job.title

        company_name = (
            company.name
            if company
            else "Company"
        )

        job_location = job.location

        is_external = False

    else:
        job_title = (
            opportunity.opportunity_title
            or "Referral opportunity"
        )

        company_name = (
            opportunity.opportunity_company
            or "Other"
        )

        job_location = None

        is_external = True

    poster = (
        db.query(User)
        .filter(
            User.id
            == opportunity.posted_by
        )
        .first()
    )

    if not poster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity owner not found",
        )

    poster_name, poster_role = (
        get_display_user(
            db,
            poster,
        )
    )

    return ReferralOpportunityResponse(
        id=opportunity.id,

        posted_by=opportunity.posted_by,
        posted_by_name=poster_name,
        posted_by_role=poster_role,

        job_id=opportunity.job_id,
        job_title=job_title,
        company_name=company_name,
        job_location=job_location,

        is_external=is_external,

        message=opportunity.message,

        max_referrals=opportunity.max_referrals,
        accepted_referrals=accepted_count,
        remaining_referrals=remaining_count,

        status=(
            opportunity.status.value
            if hasattr(
                opportunity.status,
                "value",
            )
            else str(
                opportunity.status
            )
        ),

        created_at=opportunity.created_at,
        updated_at=opportunity.updated_at,
    )


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
    # Platform job
    # --------------------------------------------------------

    if opportunity_data.job_id is not None:
        job = (
            db.query(Job)
            .filter(
                Job.id
                == opportunity_data.job_id
            )
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        opportunity_title = None
        opportunity_company = None

    # --------------------------------------------------------
    # External / Other opportunity
    # --------------------------------------------------------

    else:
        opportunity_title = (
            opportunity_data.opportunity_title
            or ""
        ).strip()

        opportunity_company = (
            opportunity_data.opportunity_company
            or ""
        ).strip()

        if not opportunity_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Opportunity title is required "
                    "for an external referral"
                ),
            )

        if not opportunity_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Company is required "
                    "for an external referral"
                ),
            )

    if (
        opportunity_data.max_referrals
        is not None
        and opportunity_data.max_referrals <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "max_referrals must be greater than 0"
            ),
        )

    opportunity = ReferralOpportunity(
        posted_by=current_user.id,
        job_id=opportunity_data.job_id,
        opportunity_title=opportunity_title,
        opportunity_company=opportunity_company,
        message=(
            opportunity_data.message.strip()
            if opportunity_data.message
            else None
        ),
        max_referrals=(
            opportunity_data.max_referrals
        ),
        status=(
            ReferralOpportunityStatus.OPEN.value
        ),
    )

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    return build_opportunity_response(
        db,
        opportunity,
    )


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
            ReferralOpportunity.job_id
            == job_id
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

    if (
        opportunity.posted_by
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the opportunity owner can update it"
            ),
        )

    update_data = opportunity_data.model_dump(
        exclude_unset=True
    )

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
        "max_referrals" in update_data
        and update_data["max_referrals"]
        is not None
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
                detail=(
                    "Status must be OPEN or CLOSED"
                ),
            )

        effective_capacity = update_data.get(
            "max_referrals",
            opportunity.max_referrals,
        )

        if (
            requested_status == "OPEN"
            and effective_capacity is not None
            and accepted_count
            >= effective_capacity
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Opportunity cannot be opened "
                    "because maximum referral capacity "
                    "has already been reached"
                ),
            )

        update_data["status"] = requested_status

    if (
        "opportunity_title"
        in update_data
        and update_data[
            "opportunity_title"
        ] is not None
    ):
        update_data[
            "opportunity_title"
        ] = update_data[
            "opportunity_title"
        ].strip()

    if (
        "opportunity_company"
        in update_data
        and update_data[
            "opportunity_company"
        ] is not None
    ):
        update_data[
            "opportunity_company"
        ] = update_data[
            "opportunity_company"
        ].strip()

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

    if (
        opportunity.posted_by
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the opportunity owner can delete it"
            ),
        )

    db.delete(opportunity)
    db.commit()

    return None
