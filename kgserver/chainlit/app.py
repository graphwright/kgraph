"""
Medical Literature Knowledge Graph — Chainlit Chat UI

Can run standalone (chainlit run app.py --host 0.0.0.0 --port 8002) or mounted
at /chat inside the kgserver API (same port as the API, no separate port).

Note: Excluded from mypy and pylint in lint.sh — Chainlit's dynamic decorators
and lack of type stubs make static analysis unreliable here.

Environment variables:
  MCP_SSE_URL       URL of the MCP SSE server (default: http://localhost/mcp/sse)
  LLM_PROVIDER      anthropic | openai | ollama  (default: anthropic)
  ANTHROPIC_MODEL   (default: claude-sonnet-4-6)
  ANTHROPIC_API_KEY
  OPENAI_MODEL      (default: gpt-4o)
  OPENAI_API_KEY
  OLLAMA_MODEL      (default: llama3.2)
  OLLAMA_BASE_URL   (default: http://ollama:11434)
  EXAMPLES_FILE     path to YAML file of example prompts (default: examples.yaml)
  MCP_CONNECT_TIMEOUT  seconds to wait for MCP connection (default: 25)
  LLM_MIN_REQUEST_INTERVAL_SECONDS  minimum seconds between the *start* of any two LLM requests (default: 3.0). Throttle is process-global so MCP/chat stays under rate limits.
  LLM_REQUEST_DELAY_SECONDS  extra delay after each LLM response (default: 0)
  LLM_RATE_LIMIT_RETRY_DELAY_SECONDS  seconds to wait before retry after rate limit (default: 20)
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


def get_litellm_model() -> dict[str, Any]:
    """Return the model string and any extra kwargs for litellm.completion."""
    if LLM_PROVIDER == "anthropic":
        return {
            "model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        }
    elif LLM_PROVIDER == "openai":
        return {
            "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
        }
    elif LLM_PROVIDER == "ollama":
        return {
            "model": f"ollama/{os.environ.get('OLLAMA_MODEL', 'llama3.2')}",
            "api_base": os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434"),
        }
    else:
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
    return {
        "BRCA mutations & cancer risk": ("What does the graph say about BRCA1/BRCA2 mutations and risk of breast and ovarian cancer, and what risk-reducing interventions are supported?"),
        "ST3Gal1 & ulcerative colitis": ("How does ST3Gal1 regulate intestinal barrier function and inflammatory cytokines in ulcerative colitis, and what downstream genes does it control?"),
        "DDR biomarkers & ES-SCLC": ("What is the DDR-Immune Fitness score, and how do HRD, TMB, and cGAS-STING predict response to PARP inhibitors and checkpoint blockers in ES-SCLC?"),
        "H. pylori → YY1 → JAK2/STAT3 → gastric cancer": ("How does H. pylori drive gastric cancer through the YY1–JAK2–STAT3 axis and EMT, and which drugs interrupt this pathway?"),
        "Bioactive glass nanoparticles & TNBC": ("What mechanisms do bioactive glass nanoparticles use against triple-negative breast cancer, and what cellular processes do they induce?"),
        "GenMine TOP vs FoundationOne in sarcoma": ("How do GenMine TOP and FoundationOne CDx compare for fusion genes and actionable targets in sarcoma, and what treatments do they enable?"),
        "Drugs linked to Type 2 Diabetes": ("What drugs are linked to or treat Type 2 Diabetes in the knowledge graph?"),
        "Genes within 1 hop of Hypothyroidism": ("What genes are connected to hypothyroidism in the graph?"),
        "Metformin and insulin resistance": ("Is there a direct relationship between metformin and insulin resistance in the literature graph?"),
        "Entities connected to Addison's disease": ("What conditions, genes, or drugs are directly connected to Addison's disease in the graph?"),
        "Documents mentioning cortisol and depression": ("Which papers in the graph mention both cortisol and depression?"),
    }


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
    model_info = get_litellm_model()["model"]
    await cl.Message(content=f"{status}\n\n**LLM:** `{provider_label}` → `{model_info}`\n\n" "Ask me anything about the medical literature knowledge graph, " "or click an example below.").send()

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


async def run_chat(user_text: str):
    history: list[dict] = cl.user_session.get("history")
    history.append({"role": "user", "content": user_text})

    mcp_session: ClientSession | None = cl.user_session.get("mcp_session")
    litellm_tools: list[dict] = cl.user_session.get("litellm_tools", [])
    llm_kwargs = get_litellm_model()

    thinking_msg = cl.Message(content=SPINNER_FRAMES[0] + " Working…")
    await thinking_msg.send()
    stop_spinner = asyncio.Event()
    spinner_task = asyncio.create_task(_run_spinner(thinking_msg, stop_spinner))

    max_iterations = 8

    try:
        for _ in range(max_iterations):
            await _throttle_llm_request()
            for attempt in range(3):
                try:
                    response = await asyncio.to_thread(
                        litellm.completion,
                        messages=history,
                        tools=litellm_tools if litellm_tools else None,
                        tool_choice="auto" if litellm_tools else None,
                        stream=False,
                        **llm_kwargs,
                    )
                    break
                except RateLimitError:
                    if attempt < 2:
                        delay = LLM_RATE_LIMIT_RETRY_DELAY_SECONDS
                        await cl.Message(content=f"⏳ Rate limited; waiting {int(delay)}s before retry…").send()
                        await asyncio.sleep(delay)
                    else:
                        raise

            if LLM_REQUEST_DELAY_SECONDS > 0:
                await asyncio.sleep(LLM_REQUEST_DELAY_SECONDS)

            msg = response.choices[0].message
            history.append(msg.model_dump(exclude_none=True))

            if msg.tool_calls:
                tool_results = await execute_tool_calls(msg.tool_calls, mcp_session)
                history.extend(tool_results)
                continue

            # Final text response
            stop_spinner.set()
            try:
                await asyncio.wait_for(spinner_task, timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                spinner_task.cancel()
                try:
                    await spinner_task
                except asyncio.CancelledError:
                    pass
            final_text = msg.content or ""
            thinking_msg.content = final_text
            await thinking_msg.update()

            if _looks_like_billing_or_rate_limit(final_text):
                await cl.Message(content="⚠️ **This response may indicate an API billing, credit, or rate limit issue.** Check your provider dashboard or API key.").send()
            break

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
