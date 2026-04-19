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

## Models & Providers

Switch between cloud providers and local LLMs using `--provider` and `--model` flags.

```bash
uv run pretty.py --provider <provider> --model <model-name>
```

### Anthropic (default)

Add your API key to `.env`:

```
ANTHROPIC_API_KEY=your-key
```

```bash
uv run pretty.py                                              # default: claude-haiku-4-5-20251001
uv run pretty.py --provider anthropic --model claude-sonnet-4-6
uv run pretty.py --provider anthropic --model claude-opus-4-7
```

### OpenAI

Add your API key to `.env`:

```
OPENAI_API_KEY=your-key
```

```bash
uv run pretty.py --provider openai --model gpt-4o
uv run pretty.py --provider openai --model gpt-4o-mini
```

> Also install the provider package: `uv add langchain-openai`

### Local LLMs via Ollama

No API key needed — runs fully offline.

1. Install [Ollama](https://ollama.com) and pull a model:

```bash
ollama pull llama3.2
ollama pull mistral
```

2. Start the server:

```bash
ollama serve
```

3. Run the agent:

```bash
uv run pretty.py --provider ollama                           # default: llama3.2
uv run pretty.py --provider ollama --model mistral
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
