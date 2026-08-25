from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SavedJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    job_id: UUID
    created_at: datetime