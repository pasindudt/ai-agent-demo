"""
Pretty CLI layer — decorators that intercept agent.py's I/O without rewriting logic.
Usage: python pretty.py
"""
import asyncio
import builtins
import functools
import agent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich import box

console = Console()


# ── decorators ────────────────────────────────────────────────────────────────

def with_status(message: str):
    """Wrap an async function with a rich status spinner."""
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            with console.status(f"[green]{message}[/green]", spinner="dots"):
                return await fn(*args, **kwargs)
        return wrapper
    return decorator


def intercept_print(fn):
    """Route plain print() calls from agent: agent replies become rich panels, rest stays."""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        original = builtins.print
        def _print(*a, **_):
            text = " ".join(str(x) for x in a)
            if text.startswith("Agent:"):
                content = text[len("Agent:"):].strip()
                console.print(Panel(Markdown(content),
                                    title="[bold bright_green]Agent[/bold bright_green]",
                                    border_style="bright_green", box=box.ROUNDED))
            else:
                console.print(text)
        builtins.print = _print
        try:
            return await fn(*args, **kwargs)
        finally:
            builtins.print = original
    return wrapper


def intercept_input(fn):
    """Replace the plain 'You: ' prompt with a styled rich prompt."""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        original = builtins.input
        builtins.input = lambda _="": original("  You › ")  # noqa: S7501 – called inside asyncio.to_thread by agent.py
        try:
            return await fn(*args, **kwargs)
        finally:
            builtins.input = original
    return wrapper


def with_invoke_spinner(fn):
    """Wrap the agent object's ainvoke with a thinking spinner."""
    @functools.wraps(fn)
    async def wrapper(ag, *args, **kwargs):
        original_ainvoke = ag.ainvoke
        async def _spinner_ainvoke(inputs, **kw):
            spinner = Spinner("dots", text="[green]Thinking…[/green]")
            with Live(spinner, console=console, refresh_per_second=12, transient=True):
                return await original_ainvoke(inputs, **kw)
        ag.ainvoke = _spinner_ainvoke
        try:
            return await fn(ag, *args, **kwargs)
        finally:
            ag.ainvoke = original_ainvoke
    return wrapper


def with_banner(fn):
    """Print the app banner before the wrapped async function runs."""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        banner = Text()
        banner.append("  AI Agent  ", style="bold white on dark_green")
        banner.append(f"  {agent.MODEL}", style="dim green")
        console.print(Panel(banner, box=box.DOUBLE_EDGE, border_style="bright_green", padding=(0, 2)))
        console.print("  [dim]Type your message and press Enter. Type [bold]exit[/bold] to quit.[/dim]\n")
        return await fn(*args, **kwargs)
    return wrapper


# ── patch & run ───────────────────────────────────────────────────────────────

_original_init_chat_model = agent.init_chat_model
def _init_with_status(*args, **kwargs):
    with console.status("[green]Initialising model…[/green]", spinner="dots"):
        return _original_init_chat_model(*args, **kwargs)
agent.init_chat_model = _init_with_status

agent.run_loop = intercept_print(intercept_input(with_invoke_spinner(agent.run_loop)))
agent.main = with_banner(agent.main)

asyncio.run(agent.main())
