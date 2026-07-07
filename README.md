# Model Context Protocol (MCP) — Complete Guide

A practical reference for understanding and building with the Model Context Protocol (MCP) — Anthropic's open standard for connecting AI models to external tools, data, and systems.

---

## Table of Contents

1. [What is MCP?](#1-what-is-mcp)
2. [Core Concepts: Client, Server, Transport, Elicitation, Sampling](#2-core-concepts)
3. [Important Imports Explained](#3-important-imports-explained)
4. [MCP Inspector — Setup & Usage](#4-mcp-inspector--setup--usage)

---

## 1. What is MCP?

**Model Context Protocol (MCP)** is an open standard, introduced by Anthropic, that defines a common way for AI applications (like Claude) to connect to external tools, databases, files, and APIs.

Before MCP, every integration (Slack, GitHub, a local database, a filesystem) needed custom, one-off glue code between the LLM and the tool. This is often called the **"N×M integration problem"** — N models × M tools = N×M custom integrations.

MCP solves this with a single, standardized protocol:

```
 AI Application (Host)  <──MCP──>  MCP Server  <──>  External System
   e.g. Claude Desktop               e.g. GitHub server      e.g. GitHub API
```

Once a tool exposes an MCP server, **any** MCP-compatible client (Claude Desktop, Claude Code, your own app) can use it without custom code.

### Key benefits
- **Standardization** — one protocol instead of N×M custom integrations
- **Reusability** — write a server once, use it from any MCP client
- **Separation of concerns** — the model doesn't need to know API details; the server handles that
- **Security boundary** — servers control exactly what's exposed to the model

### MCP Architecture (3 pieces)

| Component | Role |
|---|---|
| **Host** | The AI application the user interacts with (Claude Desktop, an IDE, your custom app) |
| **Client** | Lives inside the host; maintains a 1:1 connection with a server |
| **Server** | A lightweight program exposing specific capabilities (tools, resources, prompts) |

---

## 2. Core Concepts

MCP defines a few core building blocks. Each has a clear responsibility.

### 2.1 MCP Server

A server exposes capabilities to clients. It's typically a small, focused program — e.g., "GitHub server," "filesystem server," "database server."

**Sample syntax (FastMCP — Python):**

```python
from mcp.server.fastmcp import FastMCP

# Create a server instance
mcp = FastMCP("weather-server")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"The weather in {city} is sunny, 28°C."

@mcp.resource("config://app-settings")
def get_settings() -> str:
    """Expose read-only application settings."""
    return "theme=dark;lang=en"

@mcp.prompt()
def review_code(code: str) -> str:
    """A reusable prompt template."""
    return f"Please review this code for bugs:\n\n{code}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 2.2 MCP Client

The client lives inside the host application. It connects to exactly **one** server, handles the handshake, and forwards requests/responses.

**Sample syntax:**

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["weather_server.py"],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover available tools
            tools = await session.list_tools()
            print(tools)

            # Call a tool
            result = await session.call_tool("get_weather", {"city": "Bengaluru"})
            print(result)
```

### 2.3 Transport

Transport defines **how** messages physically move between client and server. MCP messages themselves are JSON-RPC 2.0 — transport is just the delivery mechanism.

| Transport | Use case |
|---|---|
| **stdio** | Local processes — client launches server as a subprocess, communicates over stdin/stdout. Fast, simple, no network exposure. |
| **Streamable HTTP** | Remote servers — client connects over HTTP(S), supports streaming responses. Used for deployed/hosted MCP servers. |
| ~~SSE (legacy)~~ | Older HTTP-based streaming transport, being phased out in favor of Streamable HTTP. |

**stdio transport (local):**
```python
from mcp.client.stdio import stdio_client, StdioServerParameters

params = StdioServerParameters(command="python", args=["server.py"])
async with stdio_client(params) as (read, write):
    ...
```

**Streamable HTTP transport (remote):**
```python
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("https://my-mcp-server.com/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
```

### 2.4 Elicitation

Elicitation lets a **server ask the user (via the client) for additional input** mid-operation — for example, confirming an action or requesting missing information before proceeding.

**Sample syntax:**

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("booking-server")

@mcp.tool()
async def book_flight(destination: str, ctx: Context) -> str:
    """Book a flight, confirming with the user first."""
    result = await ctx.elicit(
        message=f"Confirm booking a flight to {destination}?",
        schema={"type": "object", "properties": {"confirm": {"type": "boolean"}}}
    )
    if result.data.get("confirm"):
        return f"Flight to {destination} booked!"
    return "Booking cancelled."
```

### 2.5 Sampling

Sampling lets a **server request an LLM completion through the client** — meaning the server can "borrow" the model's intelligence without needing its own API key or model access. The client stays in control (it can approve/deny/modify the request).

**Sample syntax:**

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("summarizer-server")

@mcp.tool()
async def summarize(text: str, ctx: Context) -> str:
    """Ask the client's LLM to summarize text."""
    response = await ctx.session.create_message(
        messages=[{"role": "user", "content": {"type": "text", "text": f"Summarize: {text}"}}],
        max_tokens=200,
    )
    return response.content.text
```

---

## 3. Important Imports Explained

| Import | What it does |
|---|---|
| **`FastMCP`** (`mcp.server.fastmcp`) | High-level, decorator-based API for building MCP servers quickly. Handles boilerplate (protocol handshake, schema generation from type hints) so you just write `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()` functions. |
| **`ClientSession`** (`mcp`) | The core client-side object. Wraps a read/write stream pair and gives you high-level methods: `initialize()`, `list_tools()`, `call_tool()`, `list_resources()`, `read_resource()`, `list_prompts()`, `get_prompt()`. |
| **`StdioServerParameters`** (`mcp`) | Config object describing **how to launch a local server as a subprocess** — the command, arguments, and environment variables. Passed into `stdio_client()`. |
| **`stdio_client`** (`mcp.client.stdio`) | An async context manager that spawns the server subprocess (using `StdioServerParameters`) and returns `(read, write)` streams for use with `ClientSession`. Used for **local** servers. |
| **`streamablehttp_client`** (`mcp.client.streamable_http`) | An async context manager that connects to a **remote** MCP server over HTTP(S), returning `(read, write, get_session_id)` streams. Used for **deployed/hosted** servers. |
| **`Context`** (`mcp.server.fastmcp`) | Passed into tool functions to give access to session-level features inside a server — logging, progress reporting, elicitation (`ctx.elicit`), and sampling (`ctx.session.create_message`). |
| **`Tool` / `Resource` / `Prompt`** (`mcp.types`) | The underlying data models (Pydantic schemas) representing what a tool, resource, or prompt looks like on the wire — mostly relevant if you're working at a lower level than FastMCP. |
| **`mcp.run(transport=...)`** | The server-side entry point that starts listening — `transport="stdio"` for local, `transport="streamable-http"` for remote-hosted servers. |

### Quick mental model

```
Server side:  FastMCP  →  @mcp.tool()/@mcp.resource()/@mcp.prompt()  →  mcp.run(transport=...)
Client side:  stdio_client() or streamablehttp_client()  →  (read, write) streams  →  ClientSession
```

---

## 4. MCP Inspector — Setup & Usage

**MCP Inspector** is Anthropic's official browser-based debugging tool for MCP servers. It lets you test tools, resources, and prompts **without needing a full client like Claude Desktop** — great for development and debugging.

### 4.1 Running Inspector

No installation needed — run it directly with `npx`:

```bash
npx @modelcontextprotocol/inspector python your_server.py
```

This will:
1. Launch your MCP server as a subprocess (via stdio)
2. Start a local web UI (usually at `http://localhost:6274`)
3. Open your browser to the Inspector interface

### 4.2 For servers with dependencies (using `uv`)

```bash
npx @modelcontextprotocol/inspector uv run python your_server.py
```

### 4.3 Inspecting a remote (HTTP) server

```bash
npx @modelcontextprotocol/inspector
```
Then, in the Inspector UI, manually enter the server's URL and select **Streamable HTTP** as the transport type, instead of launching a local process.

### 4.4 What you can do inside Inspector

| Tab | Purpose |
|---|---|
| **Tools** | List all tools, view their auto-generated JSON schemas, and call them with test inputs |
| **Resources** | Browse and read exposed resources |
| **Prompts** | View and test prompt templates with sample arguments |
| **Notifications** | See real-time logs, progress updates, and errors from the server |

### 4.5 Typical debugging workflow

1. Write/update your server code (`your_server.py`)
2. Run `npx @modelcontextprotocol/inspector python your_server.py`
3. In the **Tools** tab, click **List Tools** to confirm your tool is registered correctly
4. Click a tool, fill in sample parameters, and click **Run Tool**
5. Check the response and the **Notifications** panel for errors
6. Fix issues, restart Inspector, repeat

### 4.6 Common gotchas

- Missing **docstrings** on `@mcp.tool()` functions can cause schema generation issues — always document your tools.
- If Inspector can't connect, double check the `command`/`args` match exactly how you'd run the script from the terminal.
- For `uv`-managed projects, always launch via `uv run ...` inside the Inspector command so the correct virtual environment is used.

---

## Summary Cheat Sheet

```
MCP = standard protocol connecting AI models ↔ external tools/data

Server  → exposes tools/resources/prompts   (FastMCP)
Client  → connects to ONE server            (ClientSession)
Transport → stdio (local) or Streamable HTTP (remote)
Elicitation → server asks user for input mid-task
Sampling    → server asks client's LLM for a completion

Debug everything with: npx @modelcontextprotocol/inspector <run-command>
```
