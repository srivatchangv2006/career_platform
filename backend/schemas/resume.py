from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    file_name: str
    blob_container: str
    blob_path: str
    content_type: str
    file_size_bytes: int | None
    is_primary: bool
    created_at: datetime
    updated_at: datetime