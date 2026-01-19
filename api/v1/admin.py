from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1 import deps
from models import pydantic as schemas
from models.db import Tenant, User
from services.database import get_db
import uuid

router = APIRouter()

@router.post("/tenants", response_model=schemas.TenantResponse)
async def create_tenant(
    *,
    db: Session = Depends(get_db),
    tenant_in: schemas.TenantCreate,
    auth: dict = Depends(deps.admin_required)
):
    tenant = Tenant(
        id=uuid.uuid4(),
        name=tenant_in.name,
        status="active"
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

@router.get("/tenants", response_model=list[schemas.TenantResponse])
async def list_tenants(
    db: Session = Depends(get_db),
    auth: dict = Depends(deps.admin_required)
):
    return db.query(Tenant).all()
