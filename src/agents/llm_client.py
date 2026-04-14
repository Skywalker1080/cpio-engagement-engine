"""
Model-agnostic LLM Client interface.

Currently supports Ollama for local execution, but built to be 
easily swappable to Claude or other providers in the future.
"""

import abc
import logging
import aiohttp

from src.config import LLM_PROVIDER, OLLAMA_HOST, OLLAMA_MODEL

logger = logging.getLogger("llm_client")


class LLMClient(abc.ABC):
    """Abstract base class for all LLM providers."""
    
    @abc.abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response given a system prompt and user context."""
        pass


class OllamaClient(LLMClient):
    """Ollama client for local LLM inference."""
    
    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        self.host = host.rstrip("/")
        self.model = model
        
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data.get("response", "").strip()
        except aiohttp.ClientError as exc:
            logger.error("Ollama HTTP ClientError: %s", exc)
            return "I apologize, but I am currently having trouble reaching my analytics core."
        except Exception as exc:
            logger.error("Ollama unexpected error: %s", exc)
            return "I'm experiencing a temporary processing issue."


def get_llm_client() -> LLMClient:
    """Factory function to get the configured LLM client."""
    provider = LLM_PROVIDER.lower()
    
    if provider == "ollama":
        return OllamaClient()
    # elif provider == "claude":
    #     return ClaudeClient()
    else:
        logger.warning("Unsupported LLM provider '%s', falling back to Ollama", provider)
        return OllamaClient()
