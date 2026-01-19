from typing import List, Dict, Any
from agents.llm_router import LLMRouter
from pydantic import BaseModel, Field

class EvaluationResult(BaseModel):
    faithfulness: float = Field(description="Score between 0 and 1")
    relevance: float = Field(description="Score between 0 and 1")
    hallucination: float = Field(description="Score between 0 and 1")
    explanation: str

class EvaluationService:
    def __init__(self):
        self.router = LLMRouter()

    async def evaluate_response(self, query: str, response: str, context: List[str]) -> EvaluationResult:
        model = self.router.get_model().with_structured_output(EvaluationResult)
        
        prompt = (
            f"Question: {query}\n"
            f"Answer: {response}\n"
            f"Context: {' '.join(context)}\n"
            "Evaluate the answer based on faithfulness to the context, relevance to the question, and potential hallucinations."
        )
        
        result = await model.ainvoke(prompt)
        return result
