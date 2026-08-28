from uuid import UUID

from sqlalchemy.orm import Session

from models.company import Company
from models.profile import Profile
from models.recruiter_profile import RecruiterProfile
from models.user import User


def get_public_user(
    db: Session,
    user_id: UUID,
):
    row = (
        db.query(
            User,
            Profile,
            RecruiterProfile,
            Company,
        )
        .outerjoin(
            Profile,
            Profile.user_id == User.id,
        )
        .outerjoin(
            RecruiterProfile,
            RecruiterProfile.user_id == User.id,
        )
        .outerjoin(
            Company,
            Company.id == RecruiterProfile.company_id,
        )
        .filter(
            User.id == user_id,
        )
        .first()
    )

    if not row:
        return None

    user, profile, recruiter_profile, company = row

    role = (
        user.role.value
        if hasattr(user.role, "value")
        else str(user.role)
    )

    email_prefix = (
        str(user.email)
        .split("@")[0]
        .strip()
    )

    if profile:
        display_name = profile.full_name
        headline = profile.headline
        location = profile.location
        profile_image_blob_path = (
            profile.profile_image_blob_path
        )
        company_name = None

    elif recruiter_profile:
        display_name = email_prefix
        headline = recruiter_profile.designation
        location = (
            company.location
            if company
            else None
        )
        profile_image_blob_path = None
        company_name = (
            company.name
            if company
            else None
        )

    else:
        display_name = email_prefix
        headline = None
        location = None
        profile_image_blob_path = None
        company_name = None

    return {
        "user_id": user.id,
        "email": user.email,
        "display_name": display_name,
        "handle": f"@{email_prefix}",
        "role": role,
        "headline": headline,
        "location": location,
        "profile_image_blob_path": (
            profile_image_blob_path
        ),
        "company_name": company_name,
    }


def search_public_users(
    db: Session,
    query: str,
    exclude_user_id: UUID | None = None,
    limit: int = 20,
):
    from sqlalchemy import or_

    pattern = f"%{query.strip()}%"

    user_query = (
        db.query(
            User,
            Profile,
            RecruiterProfile,
            Company,
        )
        .outerjoin(
            Profile,
            Profile.user_id == User.id,
        )
        .outerjoin(
            RecruiterProfile,
            RecruiterProfile.user_id == User.id,
        )
        .outerjoin(
            Company,
            Company.id == RecruiterProfile.company_id,
        )
        .filter(
            User.status == "ACTIVE",
            or_(
                User.email.ilike(pattern),
                Profile.full_name.ilike(pattern),
                Profile.headline.ilike(pattern),
                Profile.location.ilike(pattern),
                RecruiterProfile.designation.ilike(
                    pattern
                ),
                Company.name.ilike(pattern),
            ),
        )
    )

    if exclude_user_id is not None:
        user_query = user_query.filter(
            User.id != exclude_user_id
        )

    rows = (
        user_query
        .order_by(User.created_at.desc())
        .limit(limit)
        .all()
    )

    results = []

    for (
        user,
        profile,
        recruiter_profile,
        company,
    ) in rows:
        role = (
            user.role.value
            if hasattr(user.role, "value")
            else str(user.role)
        )

        email_prefix = (
            str(user.email)
            .split("@")[0]
            .strip()
        )

        if profile:
            display_name = profile.full_name
            headline = profile.headline
            location = profile.location
            profile_image = (
                profile.profile_image_blob_path
            )
            company_name = None

        elif recruiter_profile:
            display_name = email_prefix
            headline = (
                recruiter_profile.designation
            )
            location = (
                company.location
                if company
                else None
            )
            profile_image = None
            company_name = (
                company.name
                if company
                else None
            )

        else:
            display_name = email_prefix
            headline = None
            location = None
            profile_image = None
            company_name = None

        results.append(
            {
                "user_id": user.id,
                "display_name": display_name,
                "handle": f"@{email_prefix}",
                "role": role,
                "headline": headline,
                "location": location,
                "profile_image_blob_path": (
                    profile_image
                ),
                "company_name": company_name,
            }
        )

    return results
