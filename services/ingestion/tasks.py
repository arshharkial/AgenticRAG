from worker import celery_app
from services.ingestion.processor import TextProcessor, ImageProcessor
from services.vector_store import VectorStoreService
from services.database import SessionLocal
from models.db import IngestedObject
import os

@celery_app.task(name="process_ingestion")
def process_ingestion(object_id: str, tenant_id: str, file_path: str, content_type: str):
    db = SessionLocal()
    try:
        # 1. Select Processor
        if "text" in content_type:
            processor = TextProcessor()
        elif "image" in content_type:
            processor = ImageProcessor()
        else:
            return "Unsupported content type"

        # 2. Process
        chunks = processor.process(file_path)

        # 3. Store Embeddings
        vector_service = VectorStoreService(tenant_id)
        texts = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        for m in metadatas:
            m["object_id"] = object_id
            m["tenant_id"] = tenant_id

        vector_service.add_texts(texts, metadatas)

        # 4. Update Status
        obj = db.query(IngestedObject).get(object_id)
        if obj:
            obj.ingestion_status = "completed"
            db.commit()

    finally:
        db.close()
        # In production, we'd clean up the temporary file_path
        # if os.path.exists(file_path): os.remove(file_path)
