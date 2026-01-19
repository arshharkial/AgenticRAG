import pytest
from unittest.mock import AsyncMock
from agents.llm_router import LLMRouter
from agents.orchestrator import Orchestrator

def test_llm_router():
    router = LLMRouter()
    model = router.get_model(provider="openai")
    assert model is not None

@pytest.mark.asyncio
async def test_orchestrator_retrieve(mock_db):
    orchestrator = Orchestrator(db=mock_db, tenant_id="t1", user_id="u1")
    orchestrator.search_service.hybrid_search = AsyncMock(return_value=[{"content": "result1"}])
    
    state = {"query": "hello", "context": [], "iteration": 0}
    result = await orchestrator.retrieve(state)
    
    assert result["context"] == ["result1"]
    assert result["iteration"] == 1

@pytest.mark.asyncio
async def test_orchestrator_should_continue():
    orchestrator = Orchestrator(db=None, tenant_id="t1", user_id="u1")
    
    # Case: score too low, should retrieve
    state = {"hallucination": False, "score": 0.5, "iteration": 1}
    assert orchestrator.should_continue(state) == "retrieve"
    
    # Case: hallucination detected, should retrieve
    state = {"hallucination": True, "score": 0.9, "iteration": 1}
    assert orchestrator.should_continue(state) == "retrieve"
    
    # Case: good score, no hallucination, should end
    state = {"hallucination": False, "score": 0.8, "iteration": 1}
    assert orchestrator.should_continue(state) == "end"
    
    # Case: max iterations reached
    state = {"hallucination": True, "score": 0.5, "iteration": 3}
    assert orchestrator.should_continue(state) == "end"
