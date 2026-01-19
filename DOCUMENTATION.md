# Project Documentation

This project implements an Agentic Conversational RAG Platform designed for scale, compliance, and developer flexibility.

## 1. Architecture Overview
Refer to [DesignDocument.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/DesignDocument.md) for High-Level diagrams.

### Core Components:
- **FastAPI Backend**: Handles identity, ingestion routes, and administrative tasks.
- **LangGraph Orchestrator**: Manages autonomous agent flows with built-in self-correction nodes.
- **Multi-Modal Ingestor**: Powered by Celery and Redis to handle OCR, PDF parsing, and Hybrid indexing.
- **S3 & Pinecone Storage**: Enterprise-grade storage for raw content and multi-tenant vector namespaces.

## 2. Database Schema
Detailed schema design can be found in [DatabaseDesignDocument.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/DatabaseDesignDocument.md). 
- **Tenants**: Strict isolation at all layers.
- **Compliance**: Audit logging and user-data purging support.

## 3. Implementation Details
The technical roadmap and component details are in [IMPLEMENTATIONS.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/IMPLEMENTATIONS.md). This file documents the transition to `uv` and the specific agentic strategies used.

## 4. Usage & Integration
- **Usage Guide**: Refer to [USAGE.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/USAGE.md) for cURL examples and setup instructions.
- **Postman Collection**: Import [AgenticRag.postman_collection.json](file:///Users/arshharkial/Developer/Personal/AgenticRag/AgenticRag.postman_collection.json) to quickly test endpoints.

## 5. Walkthrough & Progress
- **Step-by-Step Journey**: See [WALKTHROUGH.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/WALKTHROUGH.md).
- **Completion Tracking**: See [TASKS.md](file:///Users/arshharkial/Developer/Personal/AgenticRag/TASKS.md).
