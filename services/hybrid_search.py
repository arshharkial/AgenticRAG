from typing import List, Dict, Any
from core.config import settings
from services.vector_store import VectorStoreService
from sqlalchemy.orm import Session
from models.db import DocumentChunk # Assuming we add this model
from sqlalchemy import text


class HybridSearchService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.vector_service = VectorStoreService(tenant_id)

    async def hybrid_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # 1. Vector Search
        vector_results = await self.vector_service.search(query, k=limit)
        
        # 2. Keyword Search (BM25 placeholder using Postgres Full-Text Search)
        # In a production environment, this would use a dedicated BM25 index or Elasticsearch
        keyword_results = self.db.execute(
            text(
                "SELECT id, content FROM search_metadata " # Placeholder table
                "WHERE tenant_id = :tenant_id AND content @@ plainto_tsquery(:query) "
                "LIMIT :limit"
            ),
            {"tenant_id": self.tenant_id, "query": query, "limit": limit}
        ).fetchall()

        # 3. Simple Reranking (Placeholder)
        # Logic: combine and de-duplicate results
        combined_results = []
        seen_ids = set()

        for res in vector_results:
            combined_results.append({
                "id": res.metadata.get("chunk_id"),
                "content": res.page_content,
                "score": 1.0, # Placeholder score
                "source": "vector"
            })
            seen_ids.add(res.metadata.get("chunk_id"))

        for res in keyword_results:
            if res.id not in seen_ids:
                combined_results.append({
                    "id": res.id,
                    "content": res.content,
                    "score": 0.8, # Placeholder score
                    "source": "keyword"
                })

        return combined_results[:limit]
