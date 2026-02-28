"""LLM client abstraction for entity and relationship extraction.

Provides a unified interface for Ollama LLM integration with tool calling support.

Rate limiting: OllamaLLMClient enforces a minimum interval between the start of any
two contiguous requests (default 3s, configurable via LLM_MIN_REQUEST_INTERVAL_SECONDS
or the min_request_interval_seconds constructor arg). The throttle is process-global
(shared across all threads and all OllamaLLMClient instances) so the server-side rate
limit is respected regardless of which code path or worker issues the request.
"""

import asyncio
import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
import json

# Process-global throttle: one lock and one "last request start" time for the whole process.
# Ensures any two LLM requests (from any thread or any OllamaLLMClient instance) are
# at least min_interval seconds apart.
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
        """Generate text completion from a prompt.

        Args:
            prompt: The input prompt text.
            temperature: Sampling temperature (0.0-2.0). Lower = more deterministic.
            max_tokens: Maximum tokens to generate (None = model default).

        Returns:
            Generated text response.
        """

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any] | list[Any]:
        """Generate structured JSON response from a prompt.

        Args:
            prompt: The input prompt text (should request JSON output).
            temperature: Sampling temperature (0.0-2.0).

        Returns:
            Parsed JSON object (dict or list).

        Raises:
            ValueError: If response is not valid JSON.
        """

    async def generate_json_with_raw(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> tuple[dict[str, Any] | list[Any], str]:
        """Generate structured JSON response AND return the raw model text.

        This is useful for debugging - you can see exactly what the LLM returned
        before parsing, which helps diagnose extraction failures.

        Default implementation calls generate_json() and returns a placeholder raw text.
        Subclasses should override if they can provide the raw response.

        Args:
            prompt: The input prompt text (should request JSON output).
            temperature: Sampling temperature (0.0-2.0).

        Returns:
            Tuple of (parsed JSON object, raw response text).
        """
        data = await self.generate_json(prompt, temperature)
        return data, "<raw unavailable>"

    async def generate_json_with_tools(
        self,
        prompt: str,
        tools: list[Callable],
        temperature: float = 0.1,
    ) -> dict[str, Any] | list[Any]:
        """Generate JSON with tool calling support.

        Default implementation falls back to generate_json without tools.
        Subclasses that support tools should override this.

        Args:
            prompt: The input prompt text.
            tools: List of callable functions the LLM can invoke.
            temperature: Sampling temperature.

        Returns:
            Parsed JSON object (dict or list).
        """
        # Default: ignore tools and use regular JSON generation
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
        timeout: float = 300.0,  # Increased timeout for slow LLM responses (5 minutes)
        min_request_interval_seconds: Optional[float] = None,
    ):
        """Initialize Ollama client.

        Args:
            model: Ollama model name (e.g., "llama3.1:8b", "llama3.1:8b")
            host: Ollama server URL
            timeout: Request timeout in seconds (default: 300)
            min_request_interval_seconds: Minimum seconds between the start of any two
                contiguous requests (rate limiting). Default from env LLM_MIN_REQUEST_INTERVAL_SECONDS (3.0).
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
        self._client = ollama.Client(host=host, timeout=timeout)

    def _ensure_interval_sync(self) -> None:
        """Ensure at least min_request_interval seconds since the last request start (process-global); sleep if needed."""
        _ensure_global_interval_sync(self._min_request_interval)

    def _parse_json_from_text(self, response_text: str) -> dict[str, Any] | list[Any]:
        """Extract and parse JSON from response text.

        Handles markdown code blocks and finds the first complete JSON structure.

        Args:
            response_text: Raw text response from the LLM.

        Returns:
            Parsed JSON object (dict or list).

        Raises:
            ValueError: If no valid JSON found in response.
        """
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        def find_matching_bracket(text: str, start: int, open_char: str, close_char: str) -> int:
            """Find the matching closing bracket for an opening bracket."""
            count = 1
            i = start + 1
            while i < len(text) and count > 0:
                if text[i] == open_char:
                    count += 1
                elif text[i] == close_char:
                    count -= 1
                i += 1
            return i if count == 0 else -1

        # Try to find JSON array first
        json_start = response_text.find("[")
        if json_start != -1:
            json_end = find_matching_bracket(response_text, json_start, "[", "]")
            if json_end != -1:
                json_text = response_text[json_start:json_end]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass

        # Try to find JSON object
        json_start = response_text.find("{")
        if json_start != -1:
            json_end = find_matching_bracket(response_text, json_start, "{", "}")
            if json_end != -1:
                json_text = response_text[json_start:json_end]
                try:
                    return json.loads(json_text)
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

        # Run synchronous ollama client in thread pool to avoid blocking
        # Use asyncio.to_thread for cleaner async execution (Python 3.9+)
        def _generate():
            return self._client.generate(
                model=self.model,
                prompt=prompt,
                options=options,
            )

        try:
            # Add timeout wrapper
            response = await asyncio.wait_for(asyncio.to_thread(_generate), timeout=self.timeout)
            return response.get("response", "").strip()
        except asyncio.TimeoutError:
            raise LLMTimeoutError(f"Ollama request timed out after {self.timeout}s")
        except Exception as e:
            print(f"Ollama generate error: {e}")
            raise

    async def _call_llm_for_json(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> str:
        """Call LLM and return raw response text (internal helper)."""

        def _generate():
            response = self._client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a biomedical entity extraction expert. Extract entities and return ONLY valid JSON in the exact format requested. Never return the original text, only the extracted entities.",
                    },
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": temperature},
            )
            return response["message"]["content"]

        try:
            await asyncio.to_thread(self._ensure_interval_sync)
            # Add timeout wrapper to prevent indefinite hangs
            response_text = await asyncio.wait_for(asyncio.to_thread(_generate), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise LLMTimeoutError(f"Ollama JSON generation timed out after {self.timeout}s")

        return response_text.strip()

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any] | list[Any]:
        """Generate structured JSON response from a prompt."""
        response_text = await self._call_llm_for_json(prompt, temperature)
        return self._parse_json_from_text(response_text)

    async def generate_json_with_raw(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> tuple[dict[str, Any] | list[Any], str]:
        """Generate structured JSON response AND return the raw model text.

        This is useful for debugging - you can see exactly what the LLM returned
        before parsing, which helps diagnose extraction failures.

        Args:
            prompt: The input prompt text (should request JSON output).
            temperature: Sampling temperature (0.0-2.0).

        Returns:
            Tuple of (parsed JSON object, raw response text).

        Raises:
            ValueError: If response is not valid JSON.
        """
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
        """Generate JSON with Ollama tool calling support.

        Handles the tool call loop: LLM requests tool → execute tool → send result → repeat.

        Args:
            prompt: The input prompt text.
            tools: List of callable functions the LLM can invoke.
            temperature: Sampling temperature.
            max_tool_iterations: Maximum number of tool call iterations to prevent infinite loops.

        Returns:
            Parsed JSON object (dict or list).
        """

        def _chat_with_tools():
            messages = [
                {
                    "role": "system",
                    "content": """You are a biomedical entity extraction expert. Extract entities and return ONLY valid JSON.

You have access to a lookup_canonical_id tool that can find canonical IDs for medical entities.
For each entity you find, call the tool to get its canonical ID.

Return format: [{"entity": "name", "type": "disease|gene|drug|protein", "confidence": 0.95, "canonical_id": "ID or null"}]""",
                },
                {"role": "user", "content": prompt},
            ]

            # Convert functions to Ollama tool format
            # Ollama v0.4+ can accept Python functions directly
            response = self._client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options={"temperature": temperature},
            )

            # Handle tool calls in a loop
            iterations = 0
            while response.get("message", {}).get("tool_calls") and iterations < max_tool_iterations:
                iterations += 1
                tool_calls = response["message"]["tool_calls"]

                # Add assistant message with tool calls
                messages.append(response["message"])

                # Execute each tool call and add results
                for tool_call in tool_calls:
                    func_name = tool_call["function"]["name"]
                    func_args = tool_call["function"]["arguments"]

                    # Find and execute the matching tool
                    result = None
                    for tool in tools:
                        if tool.__name__ == func_name:
                            try:
                                result = tool(**func_args)
                            except Exception as e:
                                result = f"Error: {e}"
                            break

                    # Add tool response to messages
                    messages.append(
                        {
                            "role": "tool",
                            "content": json.dumps(result) if result is not None else "null",
                        }
                    )

                self._ensure_interval_sync()
                # Continue conversation
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
            # If tool calling fails, fall back to regular JSON generation
            print(f"Tool calling failed, falling back to regular generation: {e}")
            return await self.generate_json(prompt, temperature)

        # Parse JSON from response (same logic as generate_json)
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
                json_text = response_text[json_start:json_end]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass

        json_start = response_text.find("{")
        if json_start != -1:
            json_end = find_matching_bracket(response_text, json_start, "{", "}")
            if json_end != -1:
                json_text = response_text[json_start:json_end]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass

        raise ValueError(f"No valid JSON found in response: {response_text[:200]}")
