from typing import Annotated, List, TypedDict, Union, Literal
from langgraph.graph import StateGraph, END
from agents.llm_router import LLMRouter
from services.hybrid_search import HybridSearchService
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    query: str
    context: List[str]
    response: str
    score: float
    hallucination: bool
    iteration: int
    tenant_id: str
    user_id: str

class GradeResponse(BaseModel):
    score: float = Field(description="Relevance score between 0 and 1")
    hallucination: bool = Field(description="True if hallucination is detected")

class Orchestrator:
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.router = LLMRouter()
        self.search_service = HybridSearchService(db, tenant_id)

    async def retrieve(self, state: AgentState):
        results = await self.search_service.hybrid_search(state["query"])
        return {"context": [r["content"] for r in results], "iteration": state.get("iteration", 0) + 1}

    async def generate(self, state: AgentState):
        model = self.router.get_model()
        context_str = "\n".join(state["context"])
        prompt = f"Using the following context, answer the question.\nContext: {context_str}\n\nQuestion: {state['query']}"
        response = await model.ainvoke(prompt)
        return {"response": response.content}

    async def evaluate(self, state: AgentState):
        model = self.router.get_model().with_structured_output(GradeResponse)
        prompt = (
            f"Question: {state['query']}\n"
            f"Response: {state['response']}\n"
            f"Context: {' '.join(state['context'])}\n"
            "Grade the response based on relevance and hallucinations."
        )
        grade = await model.ainvoke(prompt)
        return {"score": grade.score, "hallucination": grade.hallucination}

    def should_continue(self, state: AgentState) -> Literal["generate", "retrieve", "end"]:
        if state["hallucination"] or state["score"] < 0.7:
            if state["iteration"] < 3:
                return "retrieve" # Try more retrieval
        return "end"

    def build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("generate", self.generate)
        workflow.add_node("evaluate", self.evaluate)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "evaluate")
        
        workflow.add_conditional_edges(
            "evaluate",
            self.should_continue,
            {
                "retrieve": "retrieve",
                "generate": "generate",
                "end": END
            }
        )
        
        return workflow.compile()
