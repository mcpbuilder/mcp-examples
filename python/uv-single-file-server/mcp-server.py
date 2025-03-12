# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "FastMCP",
# ]
# ///

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')