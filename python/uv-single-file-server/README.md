# Python MCP Server Example (Single File)

This example demonstrates how to create a simple Model Context Protocol (MCP) server using Python with a single file. This is perfect for beginners who want to get started with MCP quickly.

## This Example

This example implements a minimal MCP server that provides a simple math tool:

- A single `add` function that adds two numbers together
- Uses the FastMCP library to simplify server creation
- Runs over stdio transport for easy integration with MCP clients

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver

## Getting Started

1. **Install the dependencies**

   This example uses [uv](https://github.com/astral-sh/uv) for dependency management. The dependencies are specified in the script header:

   ```python
   # /// script
   # requires-python = ">=3.12"
   # dependencies = [
   #     "FastMCP",
   # ]
   # ///
   ```

2. **Run the server**

   You can run the server directly with uv:

   ```bash
   uv run mcp-server.py
   ```

3. **Configure your MCP client**

   Update the `client.json` file with the correct paths for your system:

   ```json
   {
       "mcpServers": {
           "math": {
           "command": "/full/path/to/uv",
           "args": [
               "--directory",
               "/full/path/to/mcp-examples/python/single-file-server.py",
               "run",
               "-n",
               "mcp-server.py"
           ],
           "env": {}
         }
       }
   }
   ```

   Replace `/full/path/to/uv` with the actual path to your uv executable and update the directory path to match your system.

   ### Finding the Correct Paths

   #### For macOS/Linux:
   
   1. To find the path to `uv`:
      ```bash
      which uv
      ```
      
   2. To find the full path to this directory:
      ```bash
      cd /path/to/mcp-examples/python/uv-single-file-server
      pwd
      ```
      
   #### For Windows:
   
   1. For the `uv` executable:
      - Find where uv is installed (typically in `C:\Users\YourUsername\.uv\bin\uv.exe`)
      - Use the path with double backslashes: `C:\\Users\\YourUsername\\.uv\\bin\\uv.exe`
      
   2. For the directory path:
      - Navigate to the folder in File Explorer
      - Right-click in the address bar and select "Copy address"
      - Use the path with double backslashes or forward slashes
      
   Example Windows configuration:
   
   ```json
   {
       "mcpServers": {
           "math": {
           "command": "C:\\Users\\YourUsername\\.uv\\bin\\uv.exe",
           "args": [
               "--directory",
               "C:\\Path\\To\\mcp-examples\\python\\uv-single-file-server",
               "run",
               "-n",
               "mcp-server.py"
           ],
           "env": {}
         }
       }
   }
   ```

4. **Connect with an MCP client**

   You can now use any MCP-compatible client (like Claude for Desktop) to interact with your server. The server will appear as a "math" server with an "add" tool.

## Understanding the Code

The server code is intentionally simple:

```python
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
```

- We create a FastMCP server named "Demo"
- We define a tool called "add" that takes two integers and returns their sum
- We run the server using stdio transport

## Next Steps

Once you're comfortable with this example, you can:

1. Add more tools to your server
2. Implement resources and prompts
3. Try more complex MCP features
4. Check out the [MCP documentation](https://modelcontextprotocol.io) for advanced topics

## Troubleshooting

If your MCP client isn't connecting to your server:

1. Verify the paths in your `client.json` file
2. Make sure uv is installed and accessible
3. Check that your Python version is 3.12 or higher
4. Ensure FastMCP is installed correctly

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [FastMCP GitHub Repository](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Client Examples](https://modelcontextprotocol.io/clients)
