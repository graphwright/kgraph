import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

MCP_URL = "http://localhost:8000/mcp"

async def main():
    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Search for the specific entities
            for query in ["BRD7", "nasopharyngeal carcinoma", "pheochromocytoma", "CRISPR dCas9"]:
                result = await session.call_tool("search_entities", {"query": query, "limit": 3})
                print(f"\n=== search: {query} ===")
                print(result.content[0].text[:500])

asyncio.run(main())
