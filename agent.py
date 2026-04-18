import asyncio
import sys
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
MODEL_PROVIDER = "anthropic"

# Default: stdio — agent spawns mcp_server.py as a subprocess (no separate terminal needed).
# SSE mode: agent connects to an already-running server over HTTP.
#   Switch by changing the entry below, e.g.:
#   "demo": {"transport": "sse", "url": "http://localhost:8000/sse"}
MCP_SERVERS = {
    "demo": {"transport": "stdio", "command": sys.executable, "args": ["mcp_server.py"]},
}

async def load_mcp_tools(servers: dict) -> list:
    if not servers:
        print("[MCP] Disabled (no servers configured)")
        return []
    try:
        client = MultiServerMCPClient(servers)
        tools = await client.get_tools()
        print(f"[MCP] {len(tools)} tools loaded from: {list(servers.keys())}")
        return tools
    except Exception as e:
        print(f"[MCP] Unavailable — running without tools. ({e})")
        return []

THREAD_CONFIG = {"configurable": {"thread_id": "default"}}

async def run_loop(agent):
    # Greet the user by sending an initial hello so the agent lists its options
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content="hello")]},
        config=THREAD_CONFIG,
    )
    print(f"Agent: {result['messages'][-1].content}\n")

    while True:
        user_input = (await asyncio.to_thread(input, "You: ")).strip()
        if not user_input or user_input.lower() == "exit":
            break
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=THREAD_CONFIG,
        )
        print(f"Agent: {result['messages'][-1].content}\n")

async def main():
    llm = init_chat_model(MODEL, model_provider=MODEL_PROVIDER)
    tools = await load_mcp_tools(MCP_SERVERS)
    memory_check_pointer = MemorySaver()

    agent = create_agent(llm, tools, checkpointer=memory_check_pointer)
    print("\nAgent ready. Type 'exit' to quit.\n")
    await run_loop(agent)


asyncio.run(main())
