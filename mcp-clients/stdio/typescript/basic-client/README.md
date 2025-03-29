# TypeScript MCP Client Example

This is a simple TypeScript implementation of an MCP (Model Context Protocol) client that can connect to MCP servers, discover their tools, and process queries using Claude.

## Features

- Connect to MCP servers defined in a configuration file
- Discover and list available tools from each server
- Process queries using Claude and execute tool calls
- Handle tool results and continue the conversation
- Support for both command-line and interactive modes

## Prerequisites

This client requires Node.js. We recommend using Node.js version 20 or 22.

If you're using [nvm](https://github.com/nvm-sh/nvm) (Node Version Manager), you can select the appropriate version with:

```bash
# Use Node.js v20
nvm use 20

# Or use Node.js v22
nvm use 22
```

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create a `.env` file with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

3. Update the `client.json` file with the paths to your MCP servers:

```json
{
  "mcpServers": {
    "math": {
      "command": "/absolute/path/to/mcp-server.py",
      "args": [],
      "env": {}
    }
  }
}
```

4. Build the TypeScript code:

```bash
npm run build
```

## Usage

You can run the client in different ways:

### Interactive Mode

Run the client without a query to enter interactive mode:

```bash
npm start
```

or

```bash
node build/client.js
```

### Command-line Mode

Run the client with a specific query:

```bash
npm start -- --query "What is 5 + 7?"
```

or

```bash
node build/client.js --query "What is 5 + 7?"
```

### Custom Configuration

Specify a custom configuration file:

```bash
npm start -- --config /path/to/custom-config.json
```

or

```bash
node build/client.js --config /path/to/custom-config.json
```

## Example

### Using with a Math MCP Server

If you have the math MCP server running, you can ask questions like:

```
What is 25 + 17?
```

Claude will use the `add` tool from the math server to calculate the result.

## How It Works

The client follows these steps:

1. Loads the configuration file to identify MCP servers
2. Connects to each server and discovers available tools
3. Processes your query using Claude, providing the available tools
4. When Claude makes a tool call, it executes it through the appropriate MCP server
5. Returns the tool result to Claude for further processing
6. Presents the final response to you

## Customizing

You can customize this client by:

1. Adding support for additional MCP transports (e.g., SSE)
2. Implementing resource handling capabilities
3. Adding authentication mechanisms
4. Enhancing error handling and retry logic

For more information about MCP, visit the [Model Context Protocol website](https://modelcontextprotocol.io/).
