# Usage Guide - Agentic RAG Platform

This guide explains how to set up, run, and interact with the Agentic Conversational RAG Platform.

## 1. Prerequisites
- Docker & Docker Compose
- OpenAI API Key (or Anthropic)
- Pinecone API Key
- AWS S3 compatible bucket

## 2. Fast Setup

1. **Clone and Configure**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Launch Infrastructure**:
   ```bash
   docker-compose up -d --build
   ```
   This will start:
   - **Traefik**: Gateway on port 80
   - **FastAPI**: API on port 8000 (accessible via Gateway)
   - **PostgreSQL**: DB with PGVector
   - **Redis/Celery**: Background processing

## 3. API Usage Flow

### Authentication & Identity
All requests require a Bearer JWT token. The `user_id` and `tenant_id` are extracted from the JWT payload.

**How to get user_id and tenant_id?**
1. **Login**: When a user logs in via the (planned) `/api/v1/login/access-token` endpoint, the system generates a JWT.
2. **Payload**: The JWT contains:
   - `sub`: The unique identifier for the user (**user_id**).
   - `tenant_id`: The identifier for the tenant (**tenant_id**).
3. **Extraction**: The backend middleware (`deps.get_current_user_tenant`) automatically decodes this token to identify the acting user and their isolation boundary.

---

## 4. cURL Examples

Replace `{{token}}` with your actual JWT.

### A. Create a New Tenant (Admin Only)
```bash
curl -X 'POST' \
  'http://localhost/api/v1/admin/tenants' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {{token}}' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Global Corp"
}'
```

### B. Upload a Document
```bash
curl -X 'POST' \
  'http://localhost/api/v1/ingest/upload' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {{token}}' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/document.pdf;type=application/pdf'
```

### C. Chat with the Agent
```bash
curl -X 'POST' \
  'http://localhost/api/v1/chat/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {{token}}' \
  -H 'Content-Type: application/json' \
  -d '{
  "content": "What are the main findings in the uploaded document?"
}'
```

---

## 5. Evaluation Reports
Evaluation happens automatically during the chat flow. Metrics (Faithfulness, Relevance, Hallucination) are recorded in the database and can be exported as JSON or PDF via the (planned) reporting endpoints.

## 6. Testing
You can run the full suite of unit and integration tests using `uv`:
```bash
export PYTHONPATH=$PYTHONPATH:.
uv run pytest tests/
```
The suite covers security, agents, ingestion processors, and API endpoints.

## 7. GDPR Compliance
To purge user data:
- **Endpoint**: (Internal Service) `ComplianceService.purge_user_data(user_id)`
