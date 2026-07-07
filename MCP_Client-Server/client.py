import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():

    params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with stdio_client(params) as(
        read_stream,
        write_stream,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        )as session:


            #Initialize the mcp session:
            await session.initialize()
            print("\n mcp session initialized")


            #list the tools:
            tools=await session.list_tools()

            for tool in tools.tools:
                print(f" -{tool.name}")

            #mcp tools call:
            result=await session.call_tool(
                    "list_files",{
                        "path":"./MCP_Client-Server"
                    }
            )

            await session.call_tool(
                "read_file",{
                    "path":"./MCP_Client-Server/tool.txt"
                }
            )

            for content in result.content:
                print(content.text)

            
            await session.call_tool(
                "create_file",{
                    "path":"./MCP_Client-Server/task.txt",
                    "content":"Learn MCP"
                }
            )
            for content in result.content:
                print(content.text)
                

    