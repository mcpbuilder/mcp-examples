# Basic Python MCP Client

This is a simple example of a Python-based Model Context Protocol (MCP) client. It demonstrates how to connect to an MCP server and use its tools.

## Features

- Connect to an MCP server using STDIO transport
- Discover and list available tools from the server
- Process queries using Claude and execute tool calls
- Handle tool results and continue the conversation

## Requirements

- Python 3.8+
- Required packages:
  - `mcp`: The Model Context Protocol Python SDK
  - `anthropic`: The Anthropic API client for Python
  - `python-dotenv`: For managing environment variables

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Run the client with a path to an MCP server:

```bash
python client.py path/to/server_script.py
```

The client will:
1. Connect to the specified MCP server
2. List available tools from the server
3. Process a sample query using Claude
4. Execute any tool calls and handle the results

## Example

```bash
# Connect to a weather server
python client.py ../path/to/weather_server.py

# Enter a query
> What's the weather like in San Francisco?
```

## How It Works

The client follows these steps:
1. Establishes a connection to the MCP server using STDIO transport
2. Discovers available tools from the server
3. Sends a query to Claude along with the available tools
4. When Claude makes a tool call, executes it through the MCP server
5. Returns the tool result to Claude for further processing
6. Presents the final response to the user

For more information about MCP, visit the [Model Context Protocol website](https://modelcontextprotocol.io/).
