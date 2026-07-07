import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():

    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    )as (
        read_stream,
        write_stream,
        _,
    ):

        async with ClientSession(
            read_stream,
            write_stream
        )as session:


            await session.initialize()
            print("\n connected to remote connection")

            tool =await session.list_tools()
            for tool in tools.tools:
                print( f"tool :{tool.name}")

            await session.call_tool(
                "write_file",{
                    "filename":"sample.txt",
                    "content":"Hello, Remote MCP"
                }
            )



            