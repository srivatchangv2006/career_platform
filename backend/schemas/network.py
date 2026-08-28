from uuid import UUID

from pydantic import BaseModel


class NetworkUserResponse(BaseModel):
    user_id: UUID
    display_name: str
    handle: str
    role: str
    headline: str | None = None
    location: str | None = None
    profile_image_blob_path: str | None = None
    company_name: str | None = None
