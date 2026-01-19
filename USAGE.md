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

### Authentication
All requests require a Bearer JWT token. In a production setup, you would use the login flow. For testing, ensure your token contains `tenant_id` and `sub` (user_id).

### Step 1: Ingest Data
Upload a file (PDF, Image, Text) to the system.
- **Endpoint**: `POST /api/v1/ingest/upload`
- **Body**: `multipart/form-data` with `file`
- **Output**: Returns an `object_id` and `pending` status.

### Step 2: Chat with Agents
Once ingestion is complete, ask questions about your data.
- **Endpoint**: `POST /api/v1/chat/`
- **Body**: `{"content": "What is the summary of the design document?"}`
- **Output**: Returns the generated response after agentic orchestration.

### Step 3: Admin Management
Manage tenants and view usage.
- **Endpoint**: `POST /api/v1/admin/tenants`
- **Body**: `{"name": "New Tenant"}`

## 4. Evaluation Reports
Evaluation happens automatically during the chat flow. Metrics (Faithfulness, Relevance, Hallucination) are recorded in the database and can be exported as JSON or PDF via the (planned) reporting endpoints.

## 5. GDPR Compliance
To purge user data:
- **Endpoint**: (Internal Service) `ComplianceService.purge_user_data(user_id)`
