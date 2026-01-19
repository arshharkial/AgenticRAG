# Agentic Conversational RAG Platform

A production-ready, multi-tenant, agentic RAG platform supporting multi-modal ingestion and autonomous agents.

## Vision
To provide a scalable, compliant, and LLM-agnostic RAG system that handles complex conversational flows with self-correction and hybrid retrieval.

## Core Features
- **Multi-Tenant**: Strict isolation at database, vector, and storage layers.
- **Agentic**: Uses autonomous agents (LangGraph) for retrieval, evaluation, and generation.
- **Multi-Modal**: Supports Text and Images (OCR), with extensible support for Audio/Video via Celery.
- **Compliant**: Implementation of SOC2 audit logs and GDPR deletion flows.
- **Hot-Swappable**: Router support for OpenAI and Anthropic providers.

## Getting Started

### Quick Start with Docker
```bash
# 1. Setup environment
cp .env.example .env

# 2. Start the stack
docker-compose up -d --build
```

### Local Development with `uv`
```bash
# Install dependencies
uv sync

# Run the app
uvicorn main:app --reload
```

## Documentation
- **Usage & cURL**: See [USAGE.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/USAGE.md)
- **Architecture**: See [DOCUMENTATION.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/DOCUMENTATION.md)
- **Postman**: Import [AgenticRag.postman_collection.json](file:///Users/arshharkial/Developer/Personal/AgenticRag/AgenticRag.postman_collection.json)

## Progress & Journey
- **Tasks**: [TASKS.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/TASKS.md)
- **Walkthrough**: [WALKTHROUGH.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/WALKTHROUGH.md)
