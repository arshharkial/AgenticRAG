from typing import Any, Optional
from core.config import settings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class LLMRouter:
    def __init__(self, provider: str = "openai", model_name: Optional[str] = None):
        self.provider = provider
        self.model_name = model_name

    def get_model(self, **kwargs) -> Any:
        if self.provider == "openai":
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=self.model_name or "gpt-4-turbo-preview",
                **kwargs
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                model_name=self.model_name or "claude-3-opus-20240229",
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
