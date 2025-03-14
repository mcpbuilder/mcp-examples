# Universal JSON Python MCP Client

This is an example of a Python-based Model Context Protocol (MCP) client that uses a JSON configuration file to connect to MCP servers. It demonstrates how to connect to multiple MCP servers using the uv package manager.

## Features

- Connect to all MCP servers defined in a JSON configuration file
- Discover and list available tools from all servers
- Process queries using Claude and execute tool calls
- Handle tool results and continue the conversation
- Uses the uv package manager for improved dependency management

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

1. Install uv if you haven't already:
   ```bash
   curl -sSf https://astral.sh/uv/install.sh | bash
   ```

## Configuration

The client uses a JSON configuration file (`mcp-config.json`) to specify MCP server settings. You can define multiple servers in this file, and the client will connect to all of them. Here's an example configuration:

```json
{
  "mcpServers": {
    "math": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory",
        "/home/test-user/mcp-basic-python.py",
        "run",
        "-n",
        "mcp-server.py"
      ],
      "env": {}
    },
    "weather": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory",
        "/home/test-user/weather-server",
        "run",
        "-n",
        "weather-server.py"
      ],
      "env": {}
    }
  }
}
```

## Usage

Run the client with the uv package manager from the main project folder:

```bash
uv run mcp-clients/stdio/python/uv-python-universal-json-client/client.py --config /path/to/mcp-config.json
```

The client will:
1. Connect to all MCP servers defined in the configuration
2. List available tools from all servers
3. Process a sample query using Claude
4. Execute any tool calls and handle the results

## Example

```bash
# Connect to all servers using the default configuration
uv run mcp-clients/stdio/python/uv-python-universal-json-client/client.py

# Enter a query
> What's 5 + 7?
```

## How It Works

The client follows these steps:
1. Reads the server configuration from the JSON file
2. Establishes connections to all MCP servers defined in the configuration
3. Discovers available tools from all servers
4. Sends a query to Claude along with all available tools
5. When Claude makes a tool call, finds the appropriate server that has the tool and executes it
6. Returns the tool result to Claude for further processing
7. Presents the final response to the user

For more information about MCP, visit the [Model Context Protocol website](https://modelcontextprotocol.io/).
