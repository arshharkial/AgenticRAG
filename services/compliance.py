from sqlalchemy.orm import Session
from models.db import IngestedObject, ChatSession, User
from services.storage import StorageService
from services.vector_store import VectorStoreService
import uuid

class ComplianceService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.storage = StorageService(tenant_id)
        self.vector_store = VectorStoreService(tenant_id)

    async def purge_user_data(self, user_id: uuid.UUID):
        # 1. Delete Chat Sessions
        sessions = self.db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
        for session in sessions:
            self.db.delete(session)
        
        # 2. Note: Ingested objects are usually tenant-level, 
        # but if linked to a user, they should be deleted too.
        
        self.db.commit()
        return True

    async def purge_tenant_data(self):
        # 1. Delete all S3 objects
        # This would require listing all objects with the tenant prefix
        
        # 2. Delete Vector Namespace
        # pc.delete_index(index_name, namespace=self.tenant_id)
        
        # 3. Delete DB records
        # Use cascading deletes if configured, or manual purge
        
        return True
