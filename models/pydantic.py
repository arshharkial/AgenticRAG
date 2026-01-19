from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatResponse(BaseModel):
    response: str
    references: Optional[List[Dict[str, Any]]] = None

class IngestionResponse(BaseModel):
    id: UUID
    status: str
    cloudfront_url: Optional[str] = None

class TenantCreate(BaseModel):
    name: str

class TenantResponse(BaseModel):
    id: UUID
    name: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
