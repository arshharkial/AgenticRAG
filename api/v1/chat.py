from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.v1 import deps
from models import pydantic as schemas
from agents.orchestrator import Orchestrator
from services.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.ChatResponse)
async def chat(
    *,
    db: Session = Depends(get_db),
    msg: schemas.ChatMessageCreate,
    auth: dict = Depends(deps.get_current_user_tenant)
):
    orchestrator = Orchestrator(db, auth["tenant_id"], auth["user_id"])
    graph = orchestrator.build_graph()
    
    initial_state = {
        "query": msg.content,
        "context": [],
        "response": "",
        "Score": 0,
        "hallucination": False,
        "iteration": 0,
        "tenant_id": auth["tenant_id"],
        "user_id": auth["user_id"]
    }
    
    result = await graph.ainvoke(initial_state)
    return schemas.ChatResponse(response=result["response"])
