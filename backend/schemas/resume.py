from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResumeRenameRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )


class ResumeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

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

    # Product-level AI state.
    ai_analysis_status: str | None = None
