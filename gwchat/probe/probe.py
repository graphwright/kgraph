"""Probe the MCP server to understand what's reachable from breast cancer."""

import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client

MCP_URL = "http://localhost:8001/sse"


async def call(session: ClientSession, tool: str, args: dict) -> str:
    r = await session.call_tool(tool, args)
    return " ".join(
        block.text for block in r.content if hasattr(block, "text")
    )


async def main():
    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(sse_client(MCP_URL))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        print("=== search: breast cancer ===")
        print(await call(session, "search_entities", {"query": "breast cancer"}))

        print("\n=== bfs 1-hop, no filter ===")
        result = await call(session, "bfs_query", {
            "seeds": ["MeSH:D001943"],
            "max_hops": 1,
            "topology_only": True,
        })
        print(result[:2000])

        print("\n=== bfs 2-hop, node_types=[gene] ===")
        result = await call(session, "bfs_query", {
            "seeds": ["MeSH:D001943"],
            "max_hops": 2,
            "node_types": ["gene"],
        })
        print(result[:3000])

        print("\n=== search: brca1 ===")
        print(await call(session, "search_entities", {"query": "brca1"}))


asyncio.run(main())
