# Technical Deep Dive: Agentic RAG Platform (Code Level)

This document provides a comprehensive, step-by-step breakdown of how the Multi-Agent RAG Platform works. It is designed for both experienced developers and novices to understand the internal logic, data flow, and "why" behind the implementation.

---

## 1. The Ingestion Pipeline (Asynchronous & Isolated)

When you upload a file, the system doesn't process it immediately. Instead, it schedules an asynchronous "task" to handle the heavy lifting.

### Step 1: API Endpoint (`api/v1/ingestion.py`)
1. **Input**: A `multipart/form-data` file upload and a valid JWT token.
2. **Action**:
   - Extracts `tenant_id` from the token.
   - Saves the file temporarily to a staging area.
   - Creates an `IngestedObject` entry in PostgreSQL with status `pending`.
   - Triggers the Celery task: `process_ingestion.delay(object_id, tenant_id, file_path, content_type)`.
3. **Output**: Returns a `202 Accepted` response with the `object_id`.

### Step 2: The Celery Task (`services/ingestion/tasks.py`)
This is where the actual work happens in the background.

```python
@celery_app.task(name="process_ingestion")
def process_ingestion(object_id, tenant_id, file_path, content_type):
    # 1. Select the right tool for the job (Text or Image)
    if "text" in content_type: processor = TextProcessor()
    # 2. Extract content and break into chunks
    chunks = processor.process(file_path) 
    # 3. Save to the Vector Database (Pinecone) within the tenant's namespace
    vector_service = VectorStoreService(tenant_id)
    vector_service.add_texts(texts, metadatas)
    # 4. Finalize the object status
    obj.ingestion_status = "completed"
```

- **Inputs**: File path and metadata.
- **Outputs**: Chunks and embeddings stored in Pinecone and PostgreSQL.
- **Errors**: If a file is corrupted, the task catches the exception, updates the status to `failed`, and logs the error in the `AuditLog`.

---

## 2. The Hybrid Retrieval Process (Precise & Semantic)

Standard RAG often misses specific keywords or technical IDs. Our **Hybrid Search** service fixes this by combining two different search methods.

### Step 1: Vector Search (Semantic)
- **Tool**: `services/vector_store.py`
- **How**: It uses OpenAI's `text-embedding-3-small` to convert the query into a list of numbers (a vector). It then asks Pinecone: *"Which document chunks have numbers most similar to these?"*
- **Best For**: Meaning, synonyms, and context.

### Step 2: Keyword Search (Exact)
- **Tool**: `services/hybrid_search.py` (PostgreSQL Full-Text Search)
- **How**: It runs a SQL query:
  ```sql
  SELECT content FROM document_chunks 
  WHERE tenant_id = :id AND content @@ plainto_tsquery(:query)
  ```
- **Best For**: Names, technical IDs, and specific terminology.

### Step 3: Reranking & Fusion
1. **Input**: Results from both Vector and Keyword searches.
2. **Action**: It de-duplicates the lists (if a chunk appears in both) and gives a combined list sorted by relevance.
3. **Output**: A final list of the top 5 most relevant chunks.

---

## 4. The Agentic Loop (Self-Correcting Graph)

This is the "brain" of the platform. We use **LangGraph** to build a workflow that acts like a human researcher.

### The Graph Logic (`agents/orchestrator.py`)

#### Node 1: `retrieve`
- **What**: Calls the `HybridSearchService`.
- **Logic**: Fetches chunks and adds them to the "context" for the next agent.
- **Input**: User Query.
- **Output**: List of Context Chunks.

#### Node 2: `generate`
- **What**: Sends the query + context to the LLM (OpenAI/Anthropic).
- **Prompt Logic**: *"Using ONLY this context, answer the user. If you don't know, say you don't know."*
- **Input**: Query + Context.
- **Output**: A raw AI Response.

#### Node 3: `evaluate` (The Judge)
- **What**: A specialized LLM call that returns a structured "grade".
- **Parameters**:
  - `score`: How relevant is the answer? (0.0 to 1.0)
  - `hallucination`: Did the AI invent facts not in the context? (True/False)
- **Input**: Query + Context + Response.
- **Output**: A numerical score and a boolean flag.

#### Node 4: `should_continue` (The Decision Maker)
- **Logic**:
  - If `hallucination == True` OR `score < 0.7`:
    - If attempts < 3: **Go back to `retrieve`** (Try to find better info).
    - Else: **End** (We tried our best).
  - Else: **End** (Success!).

### Error Handling in Agents
- **Timeouts**: If the LLM takes too long, the orchestrator raises an `LLMTimeoutError`.
- **Bad Input**: If the user sends an empty query, the system returns a pre-defined error message without wasting LLM tokens.

---

## 5. Security & Isolation (The "Wall")

### JWT Extraction (`core/security.py`)
Every request travels with a passport (JWT). 
1. **Verification**: The system checks the signature using a `SECRET_KEY`.
2. **extraction**: It pulls out the `tenant_id`. 
3. **Enforcement**: This ID is passed to *every* service. If you are Tenant A, your queries *only ever* see `namespace="tenant-a"` in the database.

### Audit Logging
Any critical action (deleting data, creating a tenant) triggers a `db.add(AuditLog(...))` call. This is non-negotiable for SOC2 compliance.

---

## Summary for Novices
- **Think of Ingestion** as a librarian scanning books into the system while you wait.
- **Think of Retrieval** as a search engine that looks for both the exact words and the overall "meaning".
- **Think of the Agentic Loop** as a student who writes an answer, reads it, realizes they missed a point, goes back to the book to check, and then rewrites it before handing it to you.
