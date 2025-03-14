# Model Context Protocol (MCP) Examples

This repository contains example implementations of Model Context Protocol (MCP) servers and clients in different programming languages. These examples are designed to help developers get started with creating their own MCP implementations.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open standard that allows AI assistants to interact with external tools, resources, and services. MCP enables AI models to:

- **Call tools** (functions) to perform actions
- **Access resources** (data) from external sources
- **Use prompt templates** for consistent interactions

MCP creates a standardized way for AI assistants to interact with the digital world, making it easier for developers to build powerful AI-powered applications.

For a more streamlined development experience, check out [MCPBuilder.ai](https://mcpbuilder.ai) - a dedicated platform for building MCP servers.

## Repository Structure

This repository is organized into two main sections:

### MCP Servers

Servers implement the MCP specification and expose tools, resources, and prompts that AI assistants can use. We provide examples for different communication protocols:

- **STDIO Servers**: Use standard input/output for communication
  - [Python STDIO Servers](/mcp-servers/stdio/python/)
  - [TypeScript STDIO Servers](/mcp-servers/stdio/typescript/)
  
- **SSE Servers**: Use Server-Sent Events for communication
  - [Python SSE Servers](/mcp-servers/sse/python/)
  - [TypeScript SSE Servers](/mcp-servers/sse/typescript/)

### MCP Clients

Clients connect to MCP servers and allow applications to leverage the tools, resources, and prompts exposed by those servers:

- **STDIO Clients**: Connect to STDIO servers
  - [Python STDIO Clients](/mcp-clients/stdio/python/)
  - [TypeScript STDIO Clients](/mcp-clients/stdio/typescript/)
  
- **SSE Clients**: Connect to SSE servers
  - [Python SSE Clients](/mcp-clients/sse/python/)
  - [TypeScript SSE Clients](/mcp-clients/sse/typescript/)

## Getting Started

Each example directory contains its own README with specific instructions for setting up and running that example. Generally, you'll need to:

1. **Choose a server implementation** based on your preferred language and communication protocol
2. **Install dependencies** for the specific language/framework
3. **Build the server** (if necessary)
4. **Configure your MCP client** using the provided configuration files
5. **Connect with an MCP-compatible client** like Claude for Desktop or one of our example clients

## Communication Protocols

MCP supports multiple communication protocols:

- **STDIO (Standard Input/Output)**: A simple protocol where the server and client communicate through standard input and output streams. This is easy to implement and works well for local applications.

- **SSE (Server-Sent Events)**: A web protocol where the server can push updates to the client over HTTP. This is useful for web applications and services that need to maintain a persistent connection.

## Using with Claude for Desktop

[Claude for Desktop](https://claude.ai/download) is an excellent client for testing your MCP servers. To configure Claude to use your server:

1. Install Claude for Desktop
2. Create or edit the configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`
3. Add your server configuration to the file (see the example configurations in each server directory)

## Contributing

We welcome contributions to this repository! If you have an example implementation in another language or framework, please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.