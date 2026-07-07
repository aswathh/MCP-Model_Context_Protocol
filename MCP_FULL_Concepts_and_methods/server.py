from mcp.server.fastmcp import FastMCP, Context
import sys

# 1. Create server instance
mcp = FastMCP("DemoServer")

# ---------- TOOLS ----------
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool()
async def ask_ai_to_summarize(text: str, ctx: Context) -> str:
    """SAMPLING: ask client's LLM to summarize text for me."""
    result = await ctx.session.create_message(
        messages=[{"role": "user", "content": {"type": "text", "text": f"Summarize in 2 lines: {text}"}}],
        max_tokens=150,
    )
    return result.content.text

@mcp.tool()
async def book_meeting(topic: str, ctx: Context) -> str:
    """ELICITATION: ask the human user for missing info mid-execution."""
    response = await ctx.elicit(
        message=f"What date/time should I book '{topic}'?",
        schema={"type": "string"}
    )
    if response.action == "accept":
        return f"Meeting '{topic}' booked for {response.content}"
    return "Booking cancelled by user"

@mcp.tool()
async def show_client_roots(ctx: Context) -> str:
    """ROOTS: check what directories the client has exposed to me."""
    roots = await ctx.session.list_roots()
    return f"Client exposed roots: {roots}"

# ---------- RESOURCES ----------
@mcp.resource("config://server-info")
def get_server_info() -> str:
    """Static resource - read-only metadata."""
    return "DemoServer v1.0 - MCP KT example"

@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """Dynamic resource - reads a file by path param."""
    with open(path, "r") as f:
        return f.read()

# ---------- PROMPTS ----------
@mcp.prompt()
def code_review_prompt(code: str) -> str:
    """Reusable prompt template."""
    return f"Review this code and list bugs:\n\n{code}"

# ---------- RUN (TRANSPORT) ----------
if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    else:
        mcp.run(transport="stdio")