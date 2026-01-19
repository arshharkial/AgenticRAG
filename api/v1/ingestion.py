from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from api.v1 import deps
from models import pydantic as schemas
from models.db import IngestedObject, DataSource
from services.database import get_db
from services.storage import StorageService
from services.ingestion.tasks import process_ingestion
import uuid
import shutil
import os

router = APIRouter()

@router.post("/upload", response_model=schemas.IngestionResponse)
async def upload_file(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    auth: dict = Depends(deps.get_current_user_tenant)
):
    # 1. Save to S3
    storage = StorageService(auth["tenant_id"])
    file_content = await file.read()
    cloudfront_url = storage.upload_file(file_content, file.filename)
    
    # 2. Record in DB
    obj = IngestedObject(
        id=uuid.uuid4(),
        tenant_id=auth["tenant_id"],
        cloudfront_url=cloudfront_url,
        content_type=file.content_type,
        size_bytes=len(file_content),
        ingestion_status="pending"
    )
    db.add(obj)
    db.commit()
    
    # 3. Trigger Async Processing
    # For now, we save to a temp file for Celery
    temp_path = f"/tmp/{obj.id}_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(file_content)
    
    process_ingestion.delay(str(obj.id), auth["tenant_id"], temp_path, file.content_type)
    
    return schemas.IngestionResponse(
        id=obj.id, 
        status="pending", 
        cloudfront_url=cloudfront_url
    )
