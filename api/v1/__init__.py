from fastapi import APIRouter

from api.v1 import chat, ingestion, admin

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
