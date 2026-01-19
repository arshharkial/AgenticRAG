from typing import List, Optional
from core.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


class VectorStoreService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        
        if settings.PINECONE_API_KEY:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index_name = settings.PINECONE_INDEX_NAME

    def get_vector_store(self):
        # Using Pinecone as the primary vector store for now
        # Tenant isolation via namespaces
        return PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings,
            namespace=self.tenant_id
        )

    async def search(self, query: str, k: int = 5):
        store = self.get_vector_store()
        return store.similarity_search(query, k=k)

    async def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        store = self.get_vector_store()
        return store.add_texts(texts=texts, metadatas=metadatas)
