"""LLM client abstraction for entity and relationship extraction.

Provides a unified interface for Ollama LLM integration with tool calling support.

Rate limiting: OllamaLLMClient enforces a minimum interval between the start of any
two contiguous requests (default 3s, configurable via LLM_MIN_REQUEST_INTERVAL_SECONDS
or the min_request_interval_seconds constructor arg). The throttle is process-global
(shared across all threads and all OllamaLLMClient instances) so the server-side rate
limit is respected regardless of which code path or worker issues the request.
"""

import asyncio
import json
import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

# Process-global throttle: one lock and one "last request start" time for the whole process.
_global_throttle_lock = threading.Lock()
_global_last_request_time: float = 0.0


def _ensure_global_interval_sync(interval_seconds: float) -> None:
    """Ensure at least interval_seconds since the last request start (process-wide); sleep if needed."""
    global _global_last_request_time
    with _global_throttle_lock:
        now = time.monotonic()
        wait = max(0.0, _global_last_request_time + interval_seconds - now)
        _global_last_request_time = now + wait
    if wait > 0:
        time.sleep(wait)
    with _global_throttle_lock:
        _global_last_request_time = time.monotonic()


try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


DEFAULT_JSON_SYSTEM_PROMPT = (
    "You are an entity extraction expert. Extract entities and return ONLY valid JSON "
    "in the exact format requested. Never return the original text, only the extracted entities."
)

DEFAULT_TOOL_SYSTEM_PROMPT = (
    "You are an entity extraction expert. Extract entities and return ONLY valid JSON.\n\n"
    "You have access to a lookup_canonical_id tool that can find canonical IDs for entities. "
    "For each entity you find, call the tool to get its canonical ID.\n\n"
    "Return format: [{\"entity\": \"name\", \"type\": \"<entity_type>\", \"confidence\": 0.95, \"canonical_id\": \"ID or null\"}]"
)


class LLMTimeoutError(TimeoutError):
    """Raised when an LLM request (e.g. Ollama) exceeds the configured timeout.

    Ingestion should treat this as a hard failure: abort the run, do not save
    bundle or caches, and exit loudly.
    """


class LLMClientInterface(ABC):
    """Abstract interface for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text completion from a prompt."""

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any] | list[Any]:
        """Generate structured JSON response from a prompt."""

    async def generate_json_with_raw(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> tuple[dict[str, Any] | list[Any], str]:
        """Generate structured JSON response AND return the raw model text."""
        data = await self.generate_json(prompt, temperature)
        return data, "<raw unavailable>"

    async def generate_json_with_tools(
        self,
        prompt: str,
        tools: list[Callable],
        temperature: float = 0.1,
    ) -> dict[str, Any] | list[Any]:
        """Generate JSON with tool calling support. Default: fall back to generate_json."""
        return await self.generate_json(prompt, temperature)


def _default_min_request_interval() -> float:
    """Minimum seconds between the start of any two contiguous LLM requests (for rate limiting)."""
    return float(os.environ.get("LLM_MIN_REQUEST_INTERVAL_SECONDS", "3.0"))


class OllamaLLMClient(LLMClientInterface):
    """Ollama LLM client implementation."""

    def __init__(
        self,
        model: str = "llama3.1:8b",
        host: str = "http://localhost:11434",
        timeout: float = 300.0,
        min_request_interval_seconds: Optional[float] = None,
        json_system_prompt: Optional[str] = None,
        tool_system_prompt: Optional[str] = None,
    ):
        """Initialize Ollama client.

        Args:
            model: Ollama model name.
            host: Ollama server URL.
            timeout: Request timeout in seconds (default: 300).
            min_request_interval_seconds: Rate limiting interval. Default from env.
            json_system_prompt: System prompt for generate_json. Default: generic extraction expert.
            tool_system_prompt: System prompt for generate_json_with_tools. Default: generic.
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError("ollama package not installed. Install with: pip install ollama")

        self.model = model
        self.host = host
        self.timeout = timeout
        self._min_request_interval = (
            min_request_interval_seconds
            if min_request_interval_seconds is not None
            else _default_min_request_interval()
        )
        self._json_system_prompt = json_system_prompt or DEFAULT_JSON_SYSTEM_PROMPT
        self._tool_system_prompt = tool_system_prompt or DEFAULT_TOOL_SYSTEM_PROMPT
        self._client = ollama.Client(host=host, timeout=timeout)

    def _ensure_interval_sync(self) -> None:
        """Ensure at least min_request_interval seconds since the last request start (process-global)."""
        _ensure_global_interval_sync(self._min_request_interval)

    def _parse_json_from_text(self, response_text: str) -> dict[str, Any] | list[Any]:
        """Extract and parse JSON from response text."""
        response_text = response_text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        def find_matching_bracket(text: str, start: int, open_char: str, close_char: str) -> int:
            count = 1
            i = start + 1
            while i < len(text) and count > 0:
                if text[i] == open_char:
                    count += 1
                elif text[i] == close_char:
                    count -= 1
                i += 1
            return i if count == 0 else -1

        json_start = response_text.find("[")
        if json_start != -1:
            json_end = find_matching_bracket(response_text, json_start, "[", "]")
            if json_end != -1:
                try:
                    return json.loads(response_text[json_start:json_end])
                except json.JSONDecodeError:
                    pass

        json_start = response_text.find("{")
        if json_start != -1:
            json_end = find_matching_bracket(response_text, json_start, "{", "}")
            if json_end != -1:
                try:
                    return json.loads(response_text[json_start:json_end])
                except json.JSONDecodeError:
                    pass

        raise ValueError(f"No valid JSON found in response: {response_text[:200]}")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using Ollama."""
        options: dict[str, Any] = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens

        def _generate():
            return self._client.generate(model=self.model, prompt=prompt, options=options)

        try:
            response = await asyncio.wait_for(asyncio.to_thread(_generate), timeout=self.timeout)
            return response.get("response", "").strip()
        except asyncio.TimeoutError:
            raise LLMTimeoutError(f"Ollama request timed out after {self.timeout}s")
        except Exception as e:
            print(f"Ollama generate error: {e}")
            raise

    async def _call_llm_for_json(self, prompt: str, temperature: float = 0.1) -> str:
        """Call LLM and return raw response text (internal helper)."""

        def _generate():
            response = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._json_system_prompt},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": temperature},
            )
            return response["message"]["content"]

        try:
            await asyncio.to_thread(self._ensure_interval_sync)
            response_text = await asyncio.wait_for(asyncio.to_thread(_generate), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise LLMTimeoutError(f"Ollama JSON generation timed out after {self.timeout}s")

        return response_text.strip()

    async def generate_json(self, prompt: str, temperature: float = 0.1) -> dict[str, Any] | list[Any]:
        """Generate structured JSON response from a prompt."""
        response_text = await self._call_llm_for_json(prompt, temperature)
        return self._parse_json_from_text(response_text)

    async def generate_json_with_raw(
        self, prompt: str, temperature: float = 0.1
    ) -> tuple[dict[str, Any] | list[Any], str]:
        """Generate structured JSON response AND return the raw model text."""
        raw_text = await self._call_llm_for_json(prompt, temperature)
        parsed = self._parse_json_from_text(raw_text)
        return parsed, raw_text

    async def generate_json_with_tools(
        self,
        prompt: str,
        tools: list[Callable],
        temperature: float = 0.1,
        max_tool_iterations: int = 10,
    ) -> dict[str, Any] | list[Any]:
        """Generate JSON with Ollama tool calling support."""

        def _chat_with_tools():
            messages = [
                {"role": "system", "content": self._tool_system_prompt},
                {"role": "user", "content": prompt},
            ]
            response = self._client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options={"temperature": temperature},
            )

            iterations = 0
            while response.get("message", {}).get("tool_calls") and iterations < max_tool_iterations:
                iterations += 1
                tool_calls = response["message"]["tool_calls"]
                messages.append(response["message"])

                for tool_call in tool_calls:
                    func_name = tool_call["function"]["name"]
                    func_args = tool_call["function"]["arguments"]
                    if isinstance(func_args, str):
                        func_args = json.loads(func_args) if func_args else {}
                    result = None
                    for tool in tools:
                        if tool.__name__ == func_name:
                            try:
                                result = tool(**func_args)
                            except Exception as e:
                                result = f"Error: {e}"
                            break
                    messages.append(
                        {"role": "tool", "content": json.dumps(result) if result is not None else "null"}
                    )

                self._ensure_interval_sync()
                response = self._client.chat(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    options={"temperature": temperature},
                )

            return response["message"]["content"]

        try:
            response_text = await asyncio.to_thread(_chat_with_tools)
            response_text = response_text.strip()
        except Exception as e:
            print(f"Tool calling failed, falling back to regular generation: {e}")
            return await self.generate_json(prompt, temperature)

        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        def find_matching_bracket(text: str, start: int, open_char: str, close_char: str) -> int:
            count = 1
            i = start + 1
            while i < len(text) and count > 0:
                if text[i] == open_char:
                    count += 1
                elif text[i] == close_char:
                    count -= 1
                i += 1
            return i if count == 0 else -1

        json_start = response_text.find("[")
        if json_start != -1:
            json_end = find_matching_bracket(response_text, json_start, "[", "]")
            if json_end != -1:
                try:
                    return json.loads(response_text[json_start:json_end])
                except json.JSONDecodeError:
                    pass

        json_start = response_text.find("{")
        if json_start != -1:
            json_end = find_matching_bracket(response_text, json_start, "{", "}")
            if json_end != -1:
                try:
                    return json.loads(response_text[json_start:json_end])
                except json.JSONDecodeError:
                    pass

        raise ValueError(f"No valid JSON found in response: {response_text[:200]}")
