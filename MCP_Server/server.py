from mcp.server.fastmcp import FastMCP
import os
import logging

app = FastMCP("file_system")

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)




if __name__ == "__main__":
    main()
