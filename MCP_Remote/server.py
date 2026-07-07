import os
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("filesystem for remote")

BASE_DIR =Path(__file__).parent
DATA_DIR = BASE_DIR/"data"

@mcp.tool(dascription:)
def list_files(path:str):




if __name__ == "__main__":
    mcp.run(transport="streamable-http")
