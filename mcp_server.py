# MCP Server — exposes tools the agent can call
# Uses free public APIs — no extra API key needed.
#
# Run: python mcp_server.py
# Then start agent.py (MCP_SERVERS["demo"] must match this address)

import sys
import os
import argparse
from fastmcp import FastMCP
import httpx

mcp = FastMCP("Demo MCP Server")


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for any city."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://wttr.in/{city}?format=3",
            headers={"User-Agent": "curl/7.0"},
        )
        return response.text


@mcp.tool()
async def get_joke() -> str:
    """Get a random programming joke."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://official-joke-api.appspot.com/jokes/programming/random"
        )
        data = response.json()[0]
        return f"{data['setup']} — {data['punchline']}"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "sse":
        print(f"MCP server running at http://{args.host}:{args.port}/sse")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        sys.stderr = open(os.devnull, "w")
        mcp.run(transport="stdio")
