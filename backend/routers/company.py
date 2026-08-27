from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role

from models.company import Company
from models.user import User

from schemas.company import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


# ============================================================
# Recruiter/Admin: Create Company
# ============================================================

@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    existing_company = (
        db.query(Company)
        .filter(
            Company.slug == company_data.slug
        )
        .first()
    )

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company already exists",
        )

    company = Company(
        **company_data.model_dump()
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


# ============================================================
# Shared: Get Companies
# ============================================================

@router.get(
    "",
    response_model=list[CompanyResponse],
)
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        db.query(Company)
        .order_by(
            Company.name.asc()
        )
        .all()
    )


# ============================================================
# Shared: Get Company
# ============================================================

@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    company = (
        db.query(Company)
        .filter(
            Company.id == company_id
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


# ============================================================
# Recruiter/Admin: Update Company
# ============================================================

@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
)
def update_company(
    company_id: UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    company = (
        db.query(Company)
        .filter(
            Company.id == company_id
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    update_data = company_data.model_dump(
        exclude_unset=True
    )

    if "slug" in update_data:
        existing_company = (
            db.query(Company)
            .filter(
                Company.slug
                == update_data["slug"],
                Company.id != company_id,
            )
            .first()
        )

        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company slug already exists",
            )

    for field, value in update_data.items():
        setattr(
            company,
            field,
            value,
        )

    db.commit()
    db.refresh(company)

    return company