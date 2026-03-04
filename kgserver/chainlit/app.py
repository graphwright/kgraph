"""
Medical Literature Knowledge Graph — Chainlit Chat UI

Can run standalone (chainlit run app.py --host 0.0.0.0 --port 8002) or mounted
at /chat inside the kgserver API (same port as the API, no separate port).

Note: Excluded from mypy and pylint in lint.sh — Chainlit's dynamic decorators
and lack of type stubs make static analysis unreliable here.

Environment variables:
  MCP_SSE_URL       URL of the MCP SSE server (default: http://localhost/mcp/sse)
  LLM_PROVIDER      anthropic | openai | ollama  (default: anthropic)
  ANTHROPIC_MODEL   (default: claude-sonnet-4-6) — legacy single-tier
  ANTHROPIC_API_KEY, ANTHROPIC_API_KEY_1, ANTHROPIC_API_KEY_2, …  (multi-key load balancing)
  ORCHESTRATOR_MODEL  (default: claude-haiku-4-5 for anthropic, gpt-4o-mini for openai)
  SYNTHESIS_MODEL     (default: claude-sonnet-4-6 for anthropic, gpt-4o for openai)
  OPENAI_MODEL      (default: gpt-4o) — legacy single-tier
  OPENAI_API_KEY, OPENAI_API_KEY_1, …
  OLLAMA_MODEL      (default: llama3.2)
  OLLAMA_BASE_URL   (default: http://ollama:11434)
  EXAMPLES_FILE     path to YAML file of example prompts (default: examples.yaml)
  MCP_CONNECT_TIMEOUT  seconds to wait for MCP connection (default: 25)
  LLM_MIN_REQUEST_INTERVAL_SECONDS  minimum seconds between the *start* of any two LLM requests (default: 3.0)
  LLM_REQUEST_DELAY_SECONDS  extra delay after each LLM response (default: 0)
  LLM_RATE_LIMIT_RETRY_DELAY_SECONDS  seconds to wait before retry after rate limit (default: 20)
  LLM_SYNTHESIS_HISTORY_TURNS  last N turns to pass to synthesis for multi-turn context (default: 4)
"""

import asyncio
import json
import os
import time
from contextlib import AsyncExitStack
from typing import Any

import yaml
import chainlit as cl
from chainlit.input_widget import Select
import litellm
from litellm import RateLimitError
from litellm import Router
from mcp import ClientSession
from mcp.client.sse import sse_client


# Disable Chainlit DB persistence: API container sets DATABASE_URL for kgserver
# (Postgres), but we don't create Chainlit's Thread/steps tables there.
@cl.data_layer
def get_data_layer():
    return None


# ── Configuration ────────────────────────────────────────────────────────────

MCP_SSE_URL = os.environ.get("MCP_SSE_URL", "http://localhost/mcp/sse")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()
EXAMPLES_FILE = os.environ.get("EXAMPLES_FILE", "examples.yaml")
LLM_MIN_REQUEST_INTERVAL_SECONDS = float(os.environ.get("LLM_MIN_REQUEST_INTERVAL_SECONDS", "3.0"))
LLM_REQUEST_DELAY_SECONDS = float(os.environ.get("LLM_REQUEST_DELAY_SECONDS", "0"))
LLM_RATE_LIMIT_RETRY_DELAY_SECONDS = float(os.environ.get("LLM_RATE_LIMIT_RETRY_DELAY_SECONDS", "20"))

# Process-global throttle: minimum time between the *start* of any two litellm.completion calls (all chat sessions).
_llm_throttle_lock = asyncio.Lock()
_last_llm_request_start: float = 0.0


async def _throttle_llm_request() -> None:
    """Wait if needed so the next LLM request start is at least LLM_MIN_REQUEST_INTERVAL_SECONDS after the last."""
    global _last_llm_request_start
    async with _llm_throttle_lock:
        now = time.monotonic()
        wait = max(0.0, _last_llm_request_start + LLM_MIN_REQUEST_INTERVAL_SECONDS - now)
        _last_llm_request_start = now + wait
    if wait > 0:
        await asyncio.sleep(wait)
    async with _llm_throttle_lock:
        _last_llm_request_start = time.monotonic()


SYSTEM_PROMPT = """You are an expert assistant for a medical literature knowledge graph.
You have access to tools that can query a graph database of medical research papers,
extract entities, find relationships, and surface evidence for clinical questions.
Always cite the papers you draw evidence from when possible."""

ORCHESTRATOR_SYSTEM_PROMPT = """You have tools to query a medical literature knowledge graph.
Decide which tools to call to answer the user's question. Call tools as needed; when you have enough information, respond with a final answer."""

SYNTHESIS_SYSTEM_PROMPT = """You are an expert assistant. Answer the user's question using the retrieved knowledge graph evidence. Cite papers and sources when possible."""

SYNTHESIS_HISTORY_TURNS = int(os.environ.get("LLM_SYNTHESIS_HISTORY_TURNS", "4"))
ORCHESTRATOR_MAX_ITERATIONS = 8


def _collect_api_keys(prefix: str) -> list[str]:
    """Collect API keys from env: PREFIX, PREFIX_1, PREFIX_2, …"""
    keys = []
    primary = os.environ.get(prefix)
    if primary:
        keys.append(primary)
    i = 1
    while k := os.environ.get(f"{prefix}_{i}"):
        keys.append(k)
        i += 1
    return keys


def _build_model_list(
    model_name: str,
    model_str: str,
    keys: list[str],
    extra: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build model_list for Router: one deployment per key."""
    extra = extra or {}
    return [
        {
            "model_name": model_name,
            "litellm_params": {"model": model_str, "api_key": k, **extra},
        }
        for k in keys
        if k
    ]


def _get_orchestrator_model() -> str:
    """Return orchestrator model string for current provider."""
    if LLM_PROVIDER == "anthropic":
        return os.environ.get("ORCHESTRATOR_MODEL", "claude-haiku-4-5")
    if LLM_PROVIDER == "openai":
        return os.environ.get("ORCHESTRATOR_MODEL", "gpt-4o-mini")
    if LLM_PROVIDER == "ollama":
        return f"ollama/{os.environ.get('OLLAMA_MODEL', 'llama3.2')}"
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")


def _get_synthesis_model() -> str:
    """Return synthesis model string for current provider."""
    if LLM_PROVIDER == "anthropic":
        return os.environ.get("SYNTHESIS_MODEL", os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"))
    if LLM_PROVIDER == "openai":
        return os.environ.get("SYNTHESIS_MODEL", os.environ.get("OPENAI_MODEL", "gpt-4o"))
    if LLM_PROVIDER == "ollama":
        return f"ollama/{os.environ.get('OLLAMA_MODEL', 'llama3.2')}"
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")


def _create_router(model_name: str, model_str: str, routing_strategy: str = "simple-shuffle") -> Router | None:
    """Create a Router for the given model. Returns None for Ollama (no multi-key)."""
    if LLM_PROVIDER == "anthropic":
        keys = _collect_api_keys("ANTHROPIC_API_KEY")
        if not keys:
            return None
        model_list = _build_model_list(model_name, model_str, keys)
    elif LLM_PROVIDER == "openai":
        keys = _collect_api_keys("OPENAI_API_KEY")
        if not keys:
            return None
        model_list = _build_model_list(model_name, model_str, keys)
    elif LLM_PROVIDER == "ollama":
        return None
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")

    return Router(model_list=model_list, routing_strategy=routing_strategy)


_router_sentinel = object()
_orchestrator_router: Router | None = _router_sentinel  # type: ignore[assignment]  # sentinel until first call
_synthesis_router: Router | None = _router_sentinel  # type: ignore[assignment]


def _get_orchestrator_router() -> Router | None:
    """Return cached orchestrator Router, or None for Ollama. Lazy init at first call."""
    global _orchestrator_router
    if _orchestrator_router is not _router_sentinel:
        return _orchestrator_router
    _orchestrator_router = _create_router("orchestrator", _get_orchestrator_model())
    return _orchestrator_router


def _get_synthesis_router() -> Router | None:
    """Return cached synthesis Router, or None for Ollama. Lazy init at first call."""
    global _synthesis_router
    if _synthesis_router is not _router_sentinel:
        return _synthesis_router
    _synthesis_router = _create_router("synthesis", _get_synthesis_model())
    return _synthesis_router


def get_litellm_model() -> dict[str, Any]:
    """Return the model string and any extra kwargs for litellm.completion (legacy fallback)."""
    if LLM_PROVIDER == "anthropic":
        return {"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")}
    if LLM_PROVIDER == "openai":
        return {"model": os.environ.get("OPENAI_MODEL", "gpt-4o")}
    if LLM_PROVIDER == "ollama":
        return {
            "model": f"ollama/{os.environ.get('OLLAMA_MODEL', 'llama3.2')}",
            "api_base": os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434"),
        }
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")


# ── Examples ─────────────────────────────────────────────────────────────────


def load_examples() -> dict[str, str]:
    """Load examples from YAML: {label: prompt_text}"""
    try:
        with open(EXAMPLES_FILE) as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            # Support list-of-{label, prompt} dicts too
            return {item["label"]: item["prompt"] for item in data}
    except FileNotFoundError:
        pass
    # Fallback built-in examples (short versions aligned with graph content)
    # fmt: off
    return {
        "ST3Gal1 & ulcerative colitis": (
            "How does ST3Gal1 regulate intestinal barrier function and inflammatory cytokines in "
            "ulcerative colitis, and what downstream genes does it control?"
        ),
        "H. pylori → YY1 → JAK2/STAT3 → gastric cancer": (
            "How does H. pylori drive gastric cancer through the YY1-JAK2-STAT3 axis and EMT, "
            "and which drugs interrupt this pathway?"
        ),
        "DDR biomarkers & ES-SCLC": (
            "What is the DDR-Immune Fitness score, and how do HRD, TMB, and cGAS-STING predict "
            "response to PARP inhibitors and checkpoint blockers in ES-SCLC?"
        ),
        "PSMD14 → HMMR → TGF-β/PI3K in lung adenocarcinoma": (
            "How does PSMD14 stabilize HMMR through K63-deubiquitylation, and what downstream "
            "TGF-β and PI3K/AKT/mTOR effects does this produce in LUAD — and what drug combination "
            "does the graph support?"
        ),
        "PTBP1 → SLC7A11 → ferroptosis resistance in endometrial cancer": (
            "How does PTBP1 protect endometrial cancer cells from ferroptosis by stabilizing "
            "SLC7A11 mRNA, and what happens to ROS, GSH, and cell viability when PTBP1 is knocked down?"
        ),
        "BRD7 promoter methylation & CRISPR reactivation in NPC": (
            "How is BRD7 silenced by promoter hypermethylation in nasopharyngeal carcinoma, and "
            "what evidence does the graph have for reactivating it via CRISPR/dCas9-TET1CD?"
        ),
        "Pheochromocytoma → cortisol-catecholamine feedback → ectopic Cushing": (
            "How does a pheochromocytoma create a glucocorticoid-dependent positive feedback loop "
            "that drives both hypercortisolemia and hypercatecholaminemia, and what treatment sequence "
            "broke this cycle?"
        ),
    }
    # fmt: on


EXAMPLES: dict[str, str] = load_examples()
EXAMPLE_PLACEHOLDER = "— select an example —"


# ── MCP session management ────────────────────────────────────────────────────

MCP_CONNECT_TIMEOUT = float(os.environ.get("MCP_CONNECT_TIMEOUT", "25"))


async def create_mcp_session() -> tuple[ClientSession, AsyncExitStack]:
    stack = AsyncExitStack()
    read, write = await stack.enter_async_context(sse_client(MCP_SSE_URL))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session, stack


def mcp_tools_to_litellm(tools) -> list[dict]:
    """Convert MCP tool descriptors to OpenAI-style tool dicts for litellm."""
    result = []
    for t in tools:
        result.append(
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema if t.inputSchema else {"type": "object", "properties": {}},
                },
            }
        )
    return result


# ── Chainlit lifecycle ────────────────────────────────────────────────────────


@cl.on_chat_start
async def on_chat_start():
    # Show UI immediately so the page doesn't hang while connecting to MCP
    await cl.Message(content="Connecting to knowledge graph tools…").send()
    await asyncio.sleep(0)  # yield so the message is flushed to the client

    async def connect_mcp():
        session, stack = await create_mcp_session()
        tools_result = await session.list_tools()
        return session, stack, tools_result.tools

    try:
        session, stack, tools = await asyncio.wait_for(
            connect_mcp(),
            timeout=MCP_CONNECT_TIMEOUT,
        )
        cl.user_session.set("mcp_session", session)
        cl.user_session.set("mcp_stack", stack)
        cl.user_session.set("mcp_tools", tools)
        cl.user_session.set("litellm_tools", mcp_tools_to_litellm(tools))
        tool_names = [t.name for t in tools]
        status = f"✅ Connected to MCP server — {len(tools)} tools: `{'`, `'.join(tool_names)}`"
    except asyncio.TimeoutError:
        cl.user_session.set("mcp_session", None)
        cl.user_session.set("mcp_tools", [])
        cl.user_session.set("litellm_tools", [])
        status = f"⚠️ MCP server did not respond within {int(MCP_CONNECT_TIMEOUT)}s. Chat works but tools are unavailable. Try again in a moment."
    except Exception as e:
        cl.user_session.set("mcp_session", None)
        cl.user_session.set("mcp_tools", [])
        cl.user_session.set("litellm_tools", [])
        status = f"⚠️ Could not connect to MCP server ({MCP_SSE_URL}): {e}"

    # Initialize message history
    cl.user_session.set("history", [{"role": "system", "content": SYSTEM_PROMPT}])

    # Build the examples dropdown in the settings panel (gear icon)
    example_labels = [EXAMPLE_PLACEHOLDER] + list(EXAMPLES.keys())
    await cl.ChatSettings(
        [
            Select(
                id="example",
                label="📋 Example prompts",
                values=example_labels,
                initial_value=EXAMPLE_PLACEHOLDER,
            )
        ]
    ).send()

    provider_label = LLM_PROVIDER.upper()
    orch_model = _get_orchestrator_model()
    synth_model = _get_synthesis_model()
    model_info = f"orchestrator: `{orch_model}` → synthesis: `{synth_model}`" if orch_model != synth_model else orch_model
    await cl.Message(
        content=f"{status}\n\n**LLM:** `{provider_label}` → {model_info}\n\n"
        "Ask me anything about the medical literature knowledge graph, or explore the [graph visualization](/graph-viz/). "
        "Or click an example below. There is also an [e-book](https://github.com/wware/kg-book/blob/main/outline.md) in progress."
    ).send()

    # Visible example buttons in the main chat (so users don't have to open settings)
    example_actions = [cl.Action(name="run_example", label=label, payload={"prompt": prompt}) for label, prompt in EXAMPLES.items()]
    await cl.Message(content="**Example prompts:**", actions=example_actions).send()


@cl.action_callback("run_example")
async def on_example_action(action: cl.Action):
    """When user clicks an example button, send that prompt and run the chat."""
    prompt = action.payload.get("prompt") if action.payload else None
    if not prompt:
        return
    await cl.Message(content=prompt, author="User").send()
    await run_chat(prompt)
    await action.remove()


@cl.on_settings_update
async def on_settings_update(settings: dict):
    selected_label = settings.get("example", EXAMPLE_PLACEHOLDER)
    if selected_label == EXAMPLE_PLACEHOLDER:
        return

    prompt_text = EXAMPLES.get(selected_label)
    if not prompt_text:
        return

    # Show the chosen example as a user message and run it
    await cl.Message(content=prompt_text, author="User").send()
    await run_chat(prompt_text)


@cl.on_message
async def on_message(message: cl.Message):
    await run_chat(message.content)


@cl.on_chat_end
async def on_chat_end():
    stack: AsyncExitStack | None = cl.user_session.get("mcp_stack")
    if stack:
        try:
            await stack.aclose()
        except RuntimeError as e:
            # MCP SSE client uses anyio cancel scopes that must be exited in the same
            # task they were entered; on_chat_end runs in a different task than
            # on_chat_start, so graceful close is not possible. Connection will
            # be cleaned up when the client disconnects.
            if "different task" not in str(e).lower():
                raise
            # Suppress: expected when closing from on_chat_end


# ── Billing / rate-limit detection ────────────────────────────────────────────

BILLING_RATE_LIMIT_PATTERNS = (
    "billing",
    "credit",
    "rate limit",
    "quota",
    "usage limit",
    "exceeded",
    "insufficient credit",
    "payment required",
    "429",
)


def _looks_like_billing_or_rate_limit(text: str) -> bool:
    """True if the response suggests an API billing, credit, or rate-limit issue."""
    if not text or not text.strip():
        return False
    lower = text.lower()
    return any(p in lower for p in BILLING_RATE_LIMIT_PATTERNS)


# Visible spinner frames (braille pattern, one character at a time)
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
SPINNER_INTERVAL = 0.12


async def _run_spinner(msg: cl.Message, stop_event: asyncio.Event) -> None:
    """Update msg with rotating spinner + 'Working…' until stop_event is set."""
    i = 0
    while not stop_event.is_set():
        msg.content = SPINNER_FRAMES[i % len(SPINNER_FRAMES)] + " Working…"
        await msg.update()
        i += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=SPINNER_INTERVAL)
        except asyncio.TimeoutError:
            pass


# ── Core chat loop ────────────────────────────────────────────────────────────


def _truncated_history(history: list[dict], n_turns: int) -> list[dict]:
    """Return last n_turns user+assistant pairs (excluding system)."""
    non_system = [m for m in history if m.get("role") != "system"]
    keep = 2 * n_turns  # user + assistant per turn
    return non_system[-keep:] if len(non_system) > keep else non_system


def _anthropic_cache_kwargs() -> dict[str, Any]:
    """Extra kwargs for Anthropic prompt caching. Empty for other providers."""
    if LLM_PROVIDER == "anthropic":
        return {"cache_control_injection_points": [{"location": "message", "role": "system"}]}
    return {}


async def _llm_completion(
    router_model_name: str,
    messages: list[dict],
    tools: list[dict] | None = None,
) -> Any:
    """Call LLM via Router (if available) or litellm.completion. Handles retries."""
    router = _get_orchestrator_router() if router_model_name == "orchestrator" else _get_synthesis_router()
    cache_kwargs = _anthropic_cache_kwargs()

    for attempt in range(3):
        try:
            if router is not None:
                response = await router.acompletion(
                    model=router_model_name,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto" if tools else None,
                    stream=False,
                    **cache_kwargs,
                )
            else:
                model_str = _get_orchestrator_model() if router_model_name == "orchestrator" else _get_synthesis_model()
                llm_kwargs: dict[str, Any] = {"model": model_str}
                if LLM_PROVIDER == "ollama":
                    llm_kwargs["api_base"] = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
                response = await asyncio.to_thread(
                    litellm.completion,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto" if tools else None,
                    stream=False,
                    **llm_kwargs,
                    **cache_kwargs,
                )
            return response
        except RateLimitError:
            if attempt < 2:
                delay = LLM_RATE_LIMIT_RETRY_DELAY_SECONDS
                await cl.Message(content=f"⏳ Rate limited; waiting {int(delay)}s before retry…").send()
                await asyncio.sleep(delay)
            else:
                raise
    raise RuntimeError("Unreachable")


async def run_chat(user_text: str):
    history: list[dict] = cl.user_session.get("history")
    history.append({"role": "user", "content": user_text})

    mcp_session: ClientSession | None = cl.user_session.get("mcp_session")
    litellm_tools: list[dict] = cl.user_session.get("litellm_tools", [])

    thinking_msg = cl.Message(content=SPINNER_FRAMES[0] + " Working…")
    await thinking_msg.send()
    stop_spinner = asyncio.Event()
    spinner_task = asyncio.create_task(_run_spinner(thinking_msg, stop_spinner))

    tool_results_this_turn: list[dict] = []
    orchestrator_messages: list[dict] = [
        {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    try:
        # Phase A: Orchestrator tool loop (max ORCHESTRATOR_MAX_ITERATIONS)
        for iteration in range(ORCHESTRATOR_MAX_ITERATIONS):
            await _throttle_llm_request()
            response = await _llm_completion(
                router_model_name="orchestrator",
                messages=orchestrator_messages,
                tools=litellm_tools if litellm_tools else None,
            )
            if LLM_REQUEST_DELAY_SECONDS > 0:
                await asyncio.sleep(LLM_REQUEST_DELAY_SECONDS)

            msg = response.choices[0].message
            orchestrator_messages.append(msg.model_dump(exclude_none=True))

            if msg.tool_calls:
                tool_results = await execute_tool_calls(msg.tool_calls, mcp_session)
                tool_results_this_turn.extend(tool_results)
                orchestrator_messages.extend(tool_results)
                continue

            # Orchestrator returned final text (no tool calls)
            orchestrator_text = msg.content or ""

            # Phase B: Synthesis or direct return
            if tool_results_this_turn:
                # Had tool calls: run synthesis with truncated history + tool results
                truncated = _truncated_history(history, SYNTHESIS_HISTORY_TURNS)
                tool_output_str = "\n\n".join(m.get("content", "") for m in tool_results_this_turn if m.get("role") == "tool")
                synthesis_messages: list[dict] = [
                    {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                    *truncated,
                    {
                        "role": "user",
                        "content": f"{user_text}\n\n---\nRetrieved from knowledge graph:\n{tool_output_str}",
                    },
                ]
                await _throttle_llm_request()
                synth_response = await _llm_completion(
                    router_model_name="synthesis",
                    messages=synthesis_messages,
                    tools=None,
                )
                if LLM_REQUEST_DELAY_SECONDS > 0:
                    await asyncio.sleep(LLM_REQUEST_DELAY_SECONDS)
                final_text = synth_response.choices[0].message.content or ""
            else:
                # No tools needed: use orchestrator response directly
                final_text = orchestrator_text

            stop_spinner.set()
            try:
                await asyncio.wait_for(spinner_task, timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                spinner_task.cancel()
                try:
                    await spinner_task
                except asyncio.CancelledError:
                    pass
            thinking_msg.content = final_text
            await thinking_msg.update()

            if _looks_like_billing_or_rate_limit(final_text):
                await cl.Message(content="⚠️ **This response may indicate an API billing, credit, or rate limit issue.** Check your provider dashboard or API key.").send()

            history.append({"role": "assistant", "content": final_text})
            break
        else:
            # Max iterations hit without orchestrator returning final text. If we have tool
            # results, run synthesis anyway so the user gets an answer from the gathered data.
            if tool_results_this_turn:
                truncated = _truncated_history(history, SYNTHESIS_HISTORY_TURNS)
                tool_output_str = "\n\n".join(m.get("content", "") for m in tool_results_this_turn if m.get("role") == "tool")
                synthesis_messages = [
                    {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                    *truncated,
                    {
                        "role": "user",
                        "content": f"{user_text}\n\n---\nRetrieved from knowledge graph:\n{tool_output_str}",
                    },
                ]
                await _throttle_llm_request()
                synth_response = await _llm_completion(
                    router_model_name="synthesis",
                    messages=synthesis_messages,
                    tools=None,
                )
                if LLM_REQUEST_DELAY_SECONDS > 0:
                    await asyncio.sleep(LLM_REQUEST_DELAY_SECONDS)
                final_text = synth_response.choices[0].message.content or ""
            else:
                final_text = "⚠️ Maximum tool-call iterations reached. Try rephrasing your question."
            stop_spinner.set()
            try:
                await asyncio.wait_for(spinner_task, timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                spinner_task.cancel()
                try:
                    await spinner_task
                except asyncio.CancelledError:
                    pass
            thinking_msg.content = final_text
            await thinking_msg.update()
            history.append({"role": "assistant", "content": final_text})

    finally:
        stop_spinner.set()
        if not spinner_task.done():
            spinner_task.cancel()
            try:
                await spinner_task
            except asyncio.CancelledError:
                pass
    cl.user_session.set("history", history)


async def execute_tool_calls(
    tool_calls,
    mcp_session: ClientSession | None,
) -> list[dict]:
    """Run each tool call against the MCP server."""
    result_messages = []

    for tc in tool_calls:
        fn_name = tc.function.name
        try:
            fn_args = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            fn_args = {}

        tool_output: str | dict[str, Any]
        if mcp_session is None:
            tool_output = {"error": "MCP session not available"}
        else:
            try:
                mcp_result = await mcp_session.call_tool(fn_name, fn_args)
                tool_output = " ".join(block.text for block in mcp_result.content if hasattr(block, "text")) or str(mcp_result.content)
            except Exception as e:
                tool_output = f"Tool error: {e}"

        result_messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "name": fn_name,
                "content": tool_output if isinstance(tool_output, str) else json.dumps(tool_output),
            }
        )

    return result_messages
