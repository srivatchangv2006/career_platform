from uuid import UUID

from pydantic import BaseModel


class UserSearchResult(BaseModel):
    id: UUID
    display_name: str
    handle: str
    role: str
    headline: str | None = None
    location: str | None = None
    profile_image_blob_path: str | None = None
