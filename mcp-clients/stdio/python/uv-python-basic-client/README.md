# UV Python Basic MCP Client

This is a simple example of a Python-based Model Context Protocol (MCP) client that uses the `uv` package manager. It demonstrates how to connect to an MCP server and use its tools with a streamlined setup process.

## Features

- Connect to an MCP server using STDIO transport
- Discover and list available tools from the server
- Process queries using Claude and execute tool calls
- Handle tool results and continue the conversation
- **Single-file execution** with `uv` package manager

## What is UV?

[UV](https://github.com/astral-sh/uv) is a modern Python package manager built for speed and reliability. It offers several advantages:

- **Fast installation**: UV is significantly faster than pip
- **Dependency resolution**: Resolves dependencies correctly and quickly
- **Single-file scripts**: Supports running Python scripts with inline dependency declarations
- **Isolated environments**: Automatically creates and manages virtual environments

## Requirements

- Python 3.12+
- UV package manager installed (`pip install uv`)
- An Anthropic API key

## Setup

1. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

That's it! No need to manually create a virtual environment or install dependencies separately.

## Usage

Run the client with UV and a path to an MCP server:

```bash
uv run client.py path/to/server_script.py
```

The client will:
1. Automatically set up a virtual environment with the required dependencies
2. Connect to the specified MCP server
3. List available tools from the server
4. Process your queries using Claude
5. Execute any tool calls and handle the results

## Example

### Using with the UV Single File Server

Run the client with the example UV single file server:

```bash
uv run mcp-clients/stdio/python/uv-python-basic-client/client.py mcp-servers/stdio/python/uv-single-file-server/mcp-server.py 
```

You should see output like this:

```
Connecting to MCP server: mcp-servers/stdio/python/uv-single-file-server/mcp-server.py

Connected to server with tools:
  - add: Add two numbers

No query provided. Using an interactive prompt.
Enter your query (or type 'exit' to quit):
> 
```

You can then enter a query like "What is 5 + 7?" and see how the client connects to the server, Claude uses the "add" tool, and returns the result.

## How It Works

The client follows these steps:
1. UV reads the dependency declarations at the top of the script and sets up the environment
2. The client establishes a connection to the MCP server using STDIO transport
3. It discovers available tools from the server
4. It sends your query to Claude along with the available tools
5. When Claude makes a tool call, it executes it through the MCP server
6. It returns the tool result to Claude for further processing
7. It presents the final response to you

## Benefits of Using UV

- **Simplified workflow**: No need for separate requirements.txt or environment setup
- **Reproducible environments**: Dependencies are declared directly in the script
- **Faster execution**: UV's optimized dependency resolution and installation
- **Single command to run**: Just use `uv run` and you're good to go

For more information about MCP, visit the [Model Context Protocol website](https://modelcontextprotocol.io/).
For more information about UV, visit the [UV GitHub repository](https://github.com/astral-sh/uv).
