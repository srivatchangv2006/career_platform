from azure.storage.blob import BlobServiceClient

from services.azure_blob import blob_service_client


def download_blob(
    container_name: str,
    blob_path: str,
) -> bytes:
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_path,
    )

    return blob_client.download_blob().readall()