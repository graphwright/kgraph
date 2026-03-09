"""LLM backend factory for Pass 1 extraction (Anthropic, OpenAI, Ollama).

Pass 1 requires an LLM to extract entities and relationships from papers.
Set the backend via --llm-backend or LLM_BACKEND; provide API keys via
environment (ANTHROPIC_API_KEY, OPENAI_API_KEY) or .env. See LLM_SETUP.md.
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class Pass1LLMInterface(ABC):
    """Interface for Pass 1 LLM: generate JSON from system + user message."""

    @abstractmethod
    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 16384,
    ) -> dict[str, Any]:
        """Return a single JSON object (e.g. per-paper bundle)."""


def _parse_json_from_text(response_text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from response text."""
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("Unbalanced braces in JSON")


class AnthropicPass1LLM(Pass1LLMInterface):
    """Pass 1 LLM using Anthropic (Claude) API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        timeout: float = 300.0,
    ):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. pip install anthropic")
        self._client = anthropic.AsyncAnthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        self.timeout = timeout

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 16384,
    ) -> dict[str, Any]:
        response = await asyncio.wait_for(
            self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature,
            ),
            timeout=self.timeout,
        )
        text = ""
        if response.content:
            for block in response.content:
                if hasattr(block, "text"):
                    text = getattr(block, "text", "") or ""
                    break
        return _parse_json_from_text(text)


class OpenAIPass1LLM(Pass1LLMInterface):
    """Pass 1 LLM using OpenAI API or OpenAI-compatible endpoint (e.g. Lambda Labs)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: float = 300.0,
    ):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. pip install openai")
        self._client = AsyncOpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url or os.environ.get("OPENAI_API_BASE_URL"),
        )
        self.model = model
        self.timeout = timeout

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 16384,
    ) -> dict[str, Any]:
        response = await asyncio.wait_for(
            self._client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
            ),
            timeout=self.timeout,
        )
        text = (response.choices[0].message.content or "").strip()
        return _parse_json_from_text(text)


class OllamaPass1LLM(Pass1LLMInterface):
    """Pass 1 LLM using existing Ollama client (generate_json)."""

    def __init__(self, ollama_client: Any):
        """ollama_client must have async generate_json(prompt, temperature) -> dict|list."""
        self._client = ollama_client

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 16384,
    ) -> dict[str, Any]:
        combined = f"{system_prompt}\n\n---\n\n{user_message}"
        result = await self._client.generate_json(combined, temperature=temperature)
        if isinstance(result, list):
            raise ValueError("Pass 1 expects a single JSON object, not an array")
        return result


def get_pass1_llm(
    backend: str,
    *,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: float = 300.0,
    ollama_client: Optional[Any] = None,
) -> Pass1LLMInterface:
    """Return a Pass 1 LLM for the given backend.

    backend: "anthropic" | "openai" | "ollama"
    model: Override default model.
    base_url: For OpenAI-compatible endpoints (e.g. Lambda Labs).
    ollama_client: For backend "ollama", an OllamaLLMClient instance.
    """
    backend = (backend or os.environ.get("LLM_BACKEND", "ollama")).lower()
    if backend == "anthropic":
        return AnthropicPass1LLM(
            model=model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            timeout=timeout,
        )
    if backend == "openai":
        return OpenAIPass1LLM(
            model=model or os.environ.get("OPENAI_MODEL", "gpt-4o"),
            base_url=base_url or os.environ.get("OPENAI_API_BASE_URL"),
            timeout=timeout,
        )
    if backend == "ollama":
        if ollama_client is None:
            from kgraph.pipeline.llm_client import OllamaLLMClient

            ollama_client = OllamaLLMClient(
                model=os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
                host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
                timeout=timeout,
            )
        return OllamaPass1LLM(ollama_client)
    raise ValueError(f"Unknown LLM backend: {backend}. Use anthropic, openai, or ollama.")
