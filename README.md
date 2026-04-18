# AI-Agent Demo

A chat agent with MCP tool calling and RAG knowledge base.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install dependencies and create the virtual environment:

```bash
uv sync
```

Set your Anthropic API key in a `.env` file:

```bash
echo "ANTHROPIC_API_KEY=your-key" > .env
```

## Run

```bash
uv run agent.py        # plain output — great for demos and reading the code
uv run pretty.py       # rich UI — panels, spinners, styled prompts
```

The agent automatically starts `mcp_server.py` as a subprocess via **stdio** — no separate terminal needed.

Try: `What's the weather in Tokyo?` or `Tell me a joke`

### How the pretty UI works

`pretty.py` is a decorator-only layer — it never rewrites agent logic. It patches three things at runtime:

| Decorator | What it intercepts |
|---|---|
| `intercept_print` | `print("Agent: …")` → rendered as a rich Markdown panel |
| `intercept_input` | `input("You: ")` → styled `You ›` prompt |
| `with_invoke_spinner` | `agent.ainvoke(…)` → animated thinking spinner |

## Switch to SSE mode (run server separately)

SSE mode is useful when you want the MCP server to stay running across multiple agent restarts, or to share it across processes.

**Step 1** — start the server in its own terminal:

```bash
uv run mcp_server.py --transport sse
# optional flags: --host 0.0.0.0 --port 8000
```

**Step 2** — update `MCP_SERVERS` in `agent.py`:

```python
MCP_SERVERS = {
    "demo": {"transport": "sse", "url": "http://localhost:8000/sse"},
}
```

**Step 3** — run the agent as normal:

```bash
uv run agent.py
```

## Disable MCP tools

Set `MCP_SERVERS = {}` in `agent.py` to run chat-only with no tools.
