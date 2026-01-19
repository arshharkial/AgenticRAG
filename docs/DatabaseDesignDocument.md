# **Database Schema Design**

> **Rule #1:** Every table (except global admin tables) has `tenant_id`
> **Rule #2:** No raw content stored — only metadata + CloudFront URLs
> **Rule #3:** Soft deletes where legally required, hard deletes for GDPR purge

---

## 1. Tenant & Identity Layer

---

### **1.1 tenants**

```sql
tenants (
    id                  UUID PRIMARY KEY,
    name                TEXT NOT NULL,
    status              TEXT CHECK (status IN ('active','suspended','deleted')),
    created_at          TIMESTAMP,
    updated_at          TIMESTAMP,
    retention_days      INT,
    metadata            JSONB
)
```

**Purpose**

* Root isolation boundary
* Retention policies enforced here

---

### **1.2 users**

```sql
users (
    id              UUID PRIMARY KEY,
    tenant_id       UUID REFERENCES tenants(id),
    email           TEXT,
    role            TEXT CHECK (role IN ('admin','user','viewer')),
    status          TEXT,
    created_at      TIMESTAMP,
    last_login_at   TIMESTAMP
)
```

---

### **1.3 api_keys**

```sql
api_keys (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    hashed_key      TEXT,
    scope           TEXT,
    expires_at      TIMESTAMP,
    created_at      TIMESTAMP,
    revoked_at      TIMESTAMP
)
```

---

## 2. Admin & Governance Layer

---

### **2.1 system_admins (GLOBAL)**

```sql
system_admins (
    id              UUID PRIMARY KEY,
    email           TEXT UNIQUE,
    created_at      TIMESTAMP,
    immutable       BOOLEAN DEFAULT TRUE
)
```

---

### **2.2 audit_logs (SOC2 REQUIRED)**

```sql
audit_logs (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    actor_id        UUID,
    action          TEXT,
    resource_type   TEXT,
    resource_id     UUID,
    ip_address      TEXT,
    user_agent      TEXT,
    created_at      TIMESTAMP
)
```

**Best Practice**

* Write-only
* Never updated or deleted

---

## 3. Ingestion & Data Source Layer

---

### **3.1 data_sources**

```sql
data_sources (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    name            TEXT,
    type            TEXT CHECK (type IN ('text','image','audio','video')),
    created_at      TIMESTAMP,
    metadata        JSONB
)
```

---

### **3.2 ingested_objects**

```sql
ingested_objects (
    id                  UUID PRIMARY KEY,
    tenant_id           UUID,
    data_source_id      UUID,
    cloudfront_url      TEXT,
    content_type        TEXT,
    size_bytes          BIGINT,
    checksum            TEXT,
    ingestion_status    TEXT,
    created_at          TIMESTAMP
)
```

---

### **3.3 document_chunks**

```sql
document_chunks (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    object_id       UUID,
    chunk_index     INT,
    cloudfront_url  TEXT,
    embedding_id    UUID,
    metadata        JSONB
)
```

---

## 4. Vector & Retrieval Metadata Layer

---

### **4.1 embeddings_registry**

```sql
embeddings_registry (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    vector_store_id TEXT,
    model_name      TEXT,
    created_at      TIMESTAMP
)
```

---

### **4.2 search_metadata**

```sql
search_metadata (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    chunk_id        UUID,
    keywords        TEXT[],
    tags            TEXT[],
    created_at      TIMESTAMP
)
```

---

## 5. Conversational RAG Layer

---

### **5.1 chat_sessions**

```sql
chat_sessions (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    user_id         UUID,
    system_prompt   TEXT,
    summary         TEXT,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
)
```

---

### **5.2 chat_messages**

```sql
chat_messages (
    id              UUID PRIMARY KEY,
    session_id      UUID,
    role            TEXT CHECK (role IN ('user','assistant','system','tool')),
    content         TEXT,
    references      JSONB,
    created_at      TIMESTAMP
)
```

**Notes**

* `references` → chunk IDs + URLs
* Messages never mutated (audit safety)

---

## 6. Agent Orchestration Layer

---

### **6.1 agent_runs**

```sql
agent_runs (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    session_id      UUID,
    agent_type      TEXT,
    status          TEXT,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    metadata        JSONB
)
```

---

### **6.2 agent_failures**

```sql
agent_failures (
    id              UUID PRIMARY KEY,
    agent_run_id    UUID,
    error_type      TEXT,
    error_message   TEXT,
    retryable       BOOLEAN,
    created_at      TIMESTAMP
)
```

---

## 7. RAG Evaluation & Reporting

---

### **7.1 rag_evaluations**

```sql
rag_evaluations (
    id                  UUID PRIMARY KEY,
    tenant_id           UUID,
    session_id          UUID,
    query               TEXT,
    answer              TEXT,
    created_at          TIMESTAMP
)
```

---

### **7.2 rag_metrics**

```sql
rag_metrics (
    id                  UUID PRIMARY KEY,
    evaluation_id       UUID,
    faithfulness_score  FLOAT,
    relevance_score     FLOAT,
    coverage_score      FLOAT,
    hallucination_score FLOAT,
    latency_ms          INT,
    cost_usd            FLOAT
)
```

---

### **7.3 rag_reports**

```sql
rag_reports (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    evaluation_id   UUID,
    report_url      TEXT,
    created_at      TIMESTAMP
)
```

---

## 8. LLM & Model Management

---

### **8.1 llm_providers**

```sql
llm_providers (
    id              UUID PRIMARY KEY,
    name            TEXT,
    type            TEXT,
    created_at      TIMESTAMP
)
```

---

### **8.2 tenant_llm_config**

```sql
tenant_llm_config (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    provider_id     UUID,
    model_name      TEXT,
    priority        INT,
    max_tokens      INT,
    temperature     FLOAT,
    enabled         BOOLEAN
)
```

---

## 9. Quotas, Billing & Limits

---

### **9.1 tenant_quotas**

```sql
tenant_quotas (
    tenant_id           UUID PRIMARY KEY,
    max_tokens_per_day  BIGINT,
    max_ingestions_day  INT,
    max_storage_bytes  BIGINT
)
```

---

### **9.2 usage_metrics**

```sql
usage_metrics (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    date            DATE,
    tokens_used     BIGINT,
    requests        INT,
    storage_used    BIGINT
)
```

---

## 10. GDPR Compliance Layer

---

### **10.1 deletion_requests**

```sql
deletion_requests (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    user_id         UUID,
    scope           TEXT,
    status          TEXT,
    requested_at    TIMESTAMP,
    completed_at    TIMESTAMP
)
```

---

### **10.2 data_retention_jobs**

```sql
data_retention_jobs (
    id              UUID PRIMARY KEY,
    tenant_id       UUID,
    scheduled_at    TIMESTAMP,
    executed_at     TIMESTAMP,
    status          TEXT
)
```

---

## 11. Indexing & Performance Best Practices

### Required Indexes

* `(tenant_id)`
* `(tenant_id, created_at)`
* `(session_id)`
* `(evaluation_id)`

### Partitioning

* Time-based partitioning on:

  * `audit_logs`
  * `chat_messages`
  * `usage_metrics`

---
