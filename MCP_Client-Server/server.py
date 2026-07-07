from mcp.server.fastmcp import FastMCP
import os
import logging


app = FastMCP("file_system")

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)


@app.tool(description="List files and folder under the directory Path")
def list_files(path:str):
    try:
        return os.listdir(path)
    except Exception as e:
        logger.exception("Failed to list the files")
        return f"Error listing files:{e}"

@app.tool(Description="Read and return the text content of the files")
def read_file(path:str):
    try:
        with open(path,"r",encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.exception("Failed to read")
        return f"Error reading file:{e}"

def create_file(path:str,content:str):
    try:
        with open(path,"w",encoding="utf-8") as f:
            return f.write(content)
    except Exception as e:
        logger.exception(f"Failed to create file ")
        return f"Error Creating file:{e}"


if __name__ == "__main__":
    logger.info("MCP server running")
    app.run(transport="stdio")
