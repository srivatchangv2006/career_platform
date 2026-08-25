from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None
    website_url: str | None = None
    logo_blob_path: str | None = None
    industry: str | None = None
    company_size: str | None = None
    location: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    website_url: str | None = None
    logo_blob_path: str | None = None
    industry: str | None = None
    company_size: str | None = None
    location: str | None = None


class CompanyResponse(CompanyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime