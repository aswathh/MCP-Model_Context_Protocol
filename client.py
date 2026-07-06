import asyncio #for send and recieve multiple request asyncronusly

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():

    serverparamaters = StdioServerParameters(
        commands="python",
        args=["server.py"]
    )

    async with stdio_client(serverparameters) as(
        read_stream,
        write_stream
    ):

        async with ClientSession(
        read_stream,
        write_stream   
        ) as session:

#Intialise MCP session

            await session.initialize()

            print("\n MCP session is initialized")

            # list the files(for discovery)

            await session.list_tools()
            print("\n Available Tools:")

            for tool in tools.tools:
                print(f" -{tool.name}")

            # call the list_files tool

            await session.call_tool(
                "list"
            )