import os
from uuid import uuid4

from dotenv import load_dotenv
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient, ContentSettings


load_dotenv()


AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

AZURE_STORAGE_CONTAINER_NAME = os.getenv(
    "AZURE_STORAGE_CONTAINER_NAME",
    "resumes",
)


if not AZURE_STORAGE_CONNECTION_STRING:
    raise RuntimeError(
        "AZURE_STORAGE_CONNECTION_STRING is not set"
    )


blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)


def upload_resume(
    file_bytes: bytes,
    original_filename: str,
    content_type: str,
    user_id: str,
) -> str:

    safe_filename = original_filename.replace(" ", "_")

    blob_name = (
        f"users/{user_id}/resumes/"
        f"{uuid4()}_{safe_filename}"
    )

    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME,
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
            "Failed to upload resume to Azure Blob Storage"
        ) from exc

    return blob_name