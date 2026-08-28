from uuid import UUID

from pydantic import BaseModel


class PublicCompany(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    website_url: str | None = None
    logo_blob_path: str | None = None
    industry: str | None = None
    company_size: str | None = None
    location: str | None = None


class PublicPost(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str


class PublicProfileResponse(BaseModel):
    user_id: UUID
    email: str
    role: str

    full_name: str | None = None
    headline: str | None = None
    bio: str | None = None
    location: str | None = None
    years_of_experience: float | None = None
    profile_image_blob_path: str | None = None

    designation: str | None = None
    company: PublicCompany | None = None

    posts: list[PublicPost] = []
