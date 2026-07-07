import os
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("filesystem for remote")

BASE_DIR =Path(__file__).parent
DATA_DIR = BASE_DIR/"data"

@mcp.tool(description="list all the files")
def list_files():
    logging.info("listing files")
    files = os.listdir(DATA_DIR)
    return files

@mcp.tool(description="Read the file")
def read_file(filename:str):
    logging.info(f"reading this file {filename}")

    path = DATA_DIR/filename

    if not path.exists():
        return "File not found"
    with open(path,"r",encoding="utf-8")as f:
        return f.read()

@mcp.tool(description="write a new content in the file")
def write_file(filename:str,content:str):
    logging.info(f"writing the new content in this file {filename}")
    path = DATA_DIR/filename
    if not path.exists():
        return "file not found"
    with open(path,"w",encoding="utf-8")as f:
        return f.write(content)
        
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
