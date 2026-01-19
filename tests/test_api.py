import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from api.v1.deps import get_current_user_tenant, admin_required
from uuid import uuid4
from datetime import datetime

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint():
    app.dependency_overrides[get_current_user_tenant] = lambda: {"tenant_id": str(uuid4()), "user_id": "test_user"}
    
    with patch("agents.orchestrator.Orchestrator.build_graph") as mock_graph:
        mock_compiled_graph = MagicMock()
        async def mock_ainvoke(state):
            return {"response": "Mocked AI Response"}
        mock_compiled_graph.ainvoke = mock_ainvoke
        mock_graph.return_value = mock_compiled_graph
        
        response = client.post(
            "/api/v1/chat/",
            json={"content": "What is RAG?"},
            headers={"Authorization": "Bearer fake_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["response"] == "Mocked AI Response"
    
    app.dependency_overrides = {}

def test_admin_list_tenants(mock_db):
    app.dependency_overrides[admin_required] = lambda: {"role": "admin"}
    from services.database import get_db
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Use real objects or dicts that pydantic can parse
    from models.db import Tenant
    mock_tenant = Tenant(
        id=uuid4(),
        name="Tenant 1",
        status="active",
        created_at=datetime.utcnow()
    )
    
    mock_db.query.return_value.all.return_value = [mock_tenant]
    
    response = client.get(
        "/api/v1/admin/tenants",
        headers={"Authorization": "Bearer admin_token"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Tenant 1"
    
    app.dependency_overrides = {}
