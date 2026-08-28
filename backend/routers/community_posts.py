from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.community_post_images import CommunityPostImage
from models.community_posts import CommunityPost
from models.community_votes import CommunityVote, VoteType
from models.company import Company
from models.profile import Profile
from models.recruiter_profile import RecruiterProfile
from models.user import User

from schemas.community_post import (
    CommunityPostAuthorResponse,
    CommunityPostImageResponse,
    CommunityPostResponse,
    CommunityPostUpdate,
)

from services.azure_blob import blob_service_client
from services.community_image import (
    ALLOWED_IMAGE_TYPES,
    COMMUNITY_IMAGE_CONTAINER,
    MAX_IMAGE_SIZE,
    upload_community_image,
)


router = APIRouter(
    prefix="/community/posts",
    tags=["Community Posts"],
)


# ============================================================
# HELPERS
# ============================================================

def get_post_or_404(
    db: Session,
    post_id: UUID,
) -> CommunityPost:
    post = (
        db.query(CommunityPost)
        .filter(
            CommunityPost.id == post_id
        )
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community post not found",
        )

    return post


def get_post_author(
    db: Session,
    user_id: UUID,
) -> CommunityPostAuthorResponse:
    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post author not found",
        )

    role = (
        user.role.value
        if hasattr(user.role, "value")
        else str(user.role)
    )

    # --------------------------------------------------------
    # Candidate profile
    # --------------------------------------------------------

    profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == user.id
        )
        .first()
    )

    # --------------------------------------------------------
    # Recruiter profile
    # --------------------------------------------------------

    recruiter_profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == user.id
        )
        .first()
    )

    company = None

    if recruiter_profile:
        company = (
            db.query(Company)
            .filter(
                Company.id
                == recruiter_profile.company_id
            )
            .first()
        )

    # --------------------------------------------------------
    # Candidate author
    # --------------------------------------------------------

    if profile:
        return CommunityPostAuthorResponse(
            user_id=user.id,
            role=role,
            display_name=profile.full_name,
            headline=profile.headline,
            bio=profile.bio,
            location=profile.location,
            profile_image_blob_path=(
                profile.profile_image_blob_path
            ),
            designation=None,
            company_name=None,
        )

    # --------------------------------------------------------
    # Recruiter author
    #
    # RecruiterProfile currently has no full_name field,
    # so use email as the fallback display name until the
    # recruiter profile has a dedicated name field.
    # --------------------------------------------------------

    if recruiter_profile:
        return CommunityPostAuthorResponse(
            user_id=user.id,
            role=role,
            display_name=user.email,
            headline=recruiter_profile.designation,
            bio=recruiter_profile.bio,
            location=(
                company.location
                if company
                else None
            ),
            profile_image_blob_path=None,
            designation=(
                recruiter_profile.designation
            ),
            company_name=(
                company.name
                if company
                else None
            ),
        )

    # --------------------------------------------------------
    # Generic authenticated user fallback
    # --------------------------------------------------------

    return CommunityPostAuthorResponse(
        user_id=user.id,
        role=role,
        display_name=user.email,
    )


def build_post_response(
    db: Session,
    post: CommunityPost,
    current_user_id: UUID | None = None,
) -> CommunityPostResponse:
    votes = (
        db.query(CommunityVote)
        .filter(
            CommunityVote.post_id == post.id
        )
        .all()
    )

    upvotes = sum(
        1
        for vote in votes
        if vote.vote == VoteType.UP
    )

    downvotes = sum(
        1
        for vote in votes
        if vote.vote == VoteType.DOWN
    )

    user_vote = None

    if current_user_id is not None:
        existing_vote = next(
            (
                vote
                for vote in votes
                if vote.user_id == current_user_id
            ),
            None,
        )

        if existing_vote:
            user_vote = (
                existing_vote.vote.value
                if hasattr(
                    existing_vote.vote,
                    "value",
                )
                else str(
                    existing_vote.vote
                )
            )

    return CommunityPostResponse(
        id=post.id,
        user_id=post.user_id,
        author=get_post_author(
            db,
            post.user_id,
        ),
        title=post.title,
        content=post.content,
        created_at=post.created_at,
        updated_at=post.updated_at,
        upvotes=upvotes,
        downvotes=downvotes,
        user_vote=user_vote,
    )


# ============================================================
# CREATE COMMUNITY POST
#
# multipart/form-data
#
# Fields:
#   title
#   content
#   image1 (optional)
#   image2 (optional)
#   image3 (optional)
#   image4 (optional)
#   image5 (optional)
# ============================================================

@router.post(
    "",
    response_model=CommunityPostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image1: UploadFile | None = File(None),
    image2: UploadFile | None = File(None),
    image3: UploadFile | None = File(None),
    image4: UploadFile | None = File(None),
    image5: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    title = title.strip()
    content = content.strip()

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post title cannot be empty",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content cannot be empty",
        )

    post = CommunityPost(
        user_id=current_user.id,
        title=title,
        content=content,
    )

    db.add(post)
    db.flush()

    image_files = [
        image
        for image in (
            image1,
            image2,
            image3,
            image4,
            image5,
        )
        if image is not None
    ]

    uploaded_blobs: list[tuple[str, str]] = []

    try:
        for image in image_files:
            # ------------------------------------------------
            # Validate image type
            # ------------------------------------------------

            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Only JPEG, PNG, and WebP images "
                        "are allowed"
                    ),
                )

            # ------------------------------------------------
            # Read image
            # ------------------------------------------------

            file_bytes = await image.read()

            if not file_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image file is empty",
                )

            # ------------------------------------------------
            # Validate image size
            # ------------------------------------------------

            if len(file_bytes) > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Each image must be 10 MB or smaller"
                    ),
                )

            # ------------------------------------------------
            # Upload to Azure
            # ------------------------------------------------

            blob_path = upload_community_image(
                file_bytes=file_bytes,
                original_filename=(
                    image.filename or "image"
                ),
                content_type=image.content_type,
                user_id=str(current_user.id),
                post_id=str(post.id),
            )

            # ------------------------------------------------
            # Save image metadata
            # ------------------------------------------------

            image_record = CommunityPostImage(
                post_id=post.id,
                file_name=(
                    image.filename or "image"
                ),
                blob_container=(
                    COMMUNITY_IMAGE_CONTAINER
                ),
                blob_path=blob_path,
                content_type=image.content_type,
                file_size_bytes=len(file_bytes),
            )

            db.add(image_record)

            uploaded_blobs.append(
                (
                    COMMUNITY_IMAGE_CONTAINER,
                    blob_path,
                )
            )

        db.commit()
        db.refresh(post)

    except Exception:
        db.rollback()

        # ----------------------------------------------------
        # Best-effort Azure cleanup if database commit fails.
        # ----------------------------------------------------

        for container_name, blob_path in uploaded_blobs:
            try:
                blob_client = (
                    blob_service_client.get_blob_client(
                        container=container_name,
                        blob=blob_path,
                    )
                )

                if blob_client.exists():
                    blob_client.delete_blob()

            except Exception:
                pass

        raise

    return build_post_response(
        db,
        post,
        current_user.id,
    )


# ============================================================
# GET ALL COMMUNITY POSTS
# ============================================================

@router.get(
    "",
    response_model=list[CommunityPostResponse],
)
def get_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = (
        db.query(CommunityPost)
        .order_by(
            CommunityPost.created_at.desc()
        )
        .all()
    )

    return [
        build_post_response(
            db,
            post,
            current_user.id,
        )
        for post in posts
    ]


# ============================================================
# GET ALL IMAGES FOR A POST
# ============================================================

@router.get(
    "/{post_id}/images",
    response_model=list[CommunityPostImageResponse],
)
def get_post_images(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_post_or_404(
        db,
        post_id,
    )

    return (
        db.query(CommunityPostImage)
        .filter(
            CommunityPostImage.post_id == post_id
        )
        .order_by(
            CommunityPostImage.created_at.asc()
        )
        .all()
    )


# ============================================================
# GET / STREAM ONE IMAGE
# ============================================================

@router.get(
    "/{post_id}/images/{image_id}",
)
def get_post_image(
    post_id: UUID,
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = (
        db.query(CommunityPostImage)
        .filter(
            CommunityPostImage.id == image_id,
            CommunityPostImage.post_id == post_id,
        )
        .first()
    )

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community post image not found",
        )

    try:
        blob_client = (
            blob_service_client.get_blob_client(
                container=image.blob_container,
                blob=image.blob_path,
            )
        )

        if not blob_client.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found in storage",
            )

        image_bytes = (
            blob_client
            .download_blob()
            .readall()
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve image from storage",
        ) from exc

    return StreamingResponse(
        iter([image_bytes]),
        media_type=image.content_type,
        headers={
            "Content-Disposition": (
                f'inline; filename="{image.file_name}"'
            )
        },
    )


# ============================================================
# GET ONE COMMUNITY POST
# ============================================================

@router.get(
    "/{post_id}",
    response_model=CommunityPostResponse,
)
def get_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = get_post_or_404(
        db,
        post_id,
    )

    return build_post_response(
        db,
        post,
        current_user.id,
    )


# ============================================================
# UPDATE OWN COMMUNITY POST
# ============================================================

@router.put(
    "/{post_id}",
    response_model=CommunityPostResponse,
)
def update_post(
    post_id: UUID,
    post_data: CommunityPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = get_post_or_404(
        db,
        post_id,
    )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own posts",
        )

    update_data = post_data.model_dump(
        exclude_unset=True
    )

    if "title" in update_data:
        title = (
            update_data["title"] or ""
        ).strip()

        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post title cannot be empty",
            )

        update_data["title"] = title

    if "content" in update_data:
        content = (
            update_data["content"] or ""
        ).strip()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post content cannot be empty",
            )

        update_data["content"] = content

    for field, value in update_data.items():
        setattr(
            post,
            field,
            value,
        )

    post.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(post)

    return build_post_response(
        db,
        post,
        current_user.id,
    )


# ============================================================
# DELETE OWN COMMUNITY POST
# ============================================================

@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = get_post_or_404(
        db,
        post_id,
    )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts",
        )

    db.delete(post)
    db.commit()

    return None
