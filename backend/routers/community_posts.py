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
from models.user import User

from schemas.community_post import (
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

        # ----------------------------------------------------
        # Save post + image metadata
        # ----------------------------------------------------

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

    return post


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
    return (
        db.query(CommunityPost)
        .order_by(
            CommunityPost.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET ALL IMAGES FOR A POST
#
# Returns metadata only.
#
# The frontend can use image_id with the endpoint below to
# retrieve the actual image.
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
    # --------------------------------------------------------
    # Verify post exists.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Get image metadata.
    # --------------------------------------------------------

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
#
# The backend retrieves the image from Azure and streams it
# to the authenticated user.
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
    # --------------------------------------------------------
    # Find image and verify it belongs to this post.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Retrieve image from Azure Blob Storage.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Stream image to client.
    # --------------------------------------------------------

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

    return post


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

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts",
        )

    db.delete(post)
    db.commit()

    return None