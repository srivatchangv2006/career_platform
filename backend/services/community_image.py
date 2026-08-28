import os
from uuid import uuid4

from azure.core.exceptions import AzureError
from azure.storage.blob import ContentSettings

from services.azure_blob import blob_service_client


COMMUNITY_IMAGE_CONTAINER = os.getenv(
    "AZURE_COMMUNITY_IMAGE_CONTAINER",
    "community-images",
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


def upload_community_image(
    file_bytes: bytes,
    original_filename: str,
    content_type: str,
    user_id: str,
    post_id: str,
) -> str:
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "Only JPEG, PNG, and WebP images are allowed"
        )

    if not file_bytes:
        raise ValueError(
            "Image file is empty"
        )

    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(
            "Image exceeds the 10 MB limit"
        )

    safe_filename = (
        (original_filename or "image")
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    blob_name = (
        f"users/{user_id}/posts/{post_id}/"
        f"{uuid4()}_{safe_filename}"
    )

    blob_client = blob_service_client.get_blob_client(
        container=COMMUNITY_IMAGE_CONTAINER,
        blob=blob_name,
    )

    try:
        blob_client.upload_blob(
            file_bytes,
            overwrite=False,
            content_settings=ContentSettings(
                content_type=content_type
            ),
        )
    except AzureError as exc:
        raise RuntimeError(
            "Failed to upload community image"
        ) from exc

    return blob_name
