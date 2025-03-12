# Model Context Protocol (MCP) Examples

This repository contains example implementations of Model Context Protocol (MCP) servers in different programming languages. These examples are designed to help beginners get started with creating their own MCP servers.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open standard that allows AI assistants to interact with external tools, resources, and services. MCP enables AI models to:

- **Call tools** (functions) to perform actions
- **Access resources** (data) from external sources
- **Use prompt templates** for consistent interactions

MCP creates a standardized way for AI assistants to interact with the digital world, making it easier for developers to build powerful AI-powered applications.

## Examples in this Repository

### Python Examples

- [**Single-File Server (uv)**](./python/uv-single-file-server/): A minimal MCP server implemented in a single Python file using the FastMCP library and uv package manager. Perfect for beginners!

### TypeScript Examples

- [**Simple Server**](./typescript/simple-server/): A basic MCP server implemented in TypeScript that demonstrates tools, resources, and prompts using the official MCP TypeScript SDK.

## Getting Started

Each example directory contains its own README with specific instructions for setting up and running that example. Generally, you'll need to:

1. **Install dependencies** for the specific language/framework
2. **Build the server** (if necessary)
3. **Configure your MCP client** using the provided `client.json` file
4. **Connect with an MCP-compatible client** like Claude for Desktop

## Using with Claude for Desktop

[Claude for Desktop](https://claude.ai/download) is an excellent client for testing your MCP servers. To configure Claude to use your server:

1. Install Claude for Desktop
2. Create or edit the configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
3. Add your server configuration (see example below)
4. Restart Claude for Desktop

Example configuration for macOS:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "/path/to/executable",
      "args": ["arg1", "arg2"],
      "env": {}
    }
  }
}
```

Example configuration for Windows:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "C:\\Path\\To\\executable.exe",
      "args": ["arg1", "arg2"],
      "env": {}
    }
  }
}
```

### Finding File Paths

Finding the correct file paths is often the most challenging part for beginners. Here's how to get the full path to files on different operating systems:

#### macOS
1. Open Terminal
2. Navigate to your file: `cd path/to/directory`
3. Get the full path: `pwd` for the directory, then add the filename
4. For executables like `uv`, use: `which uv`

#### Windows
1. Open File Explorer and navigate to your file
2. Right-click on the file and select "Properties"
3. The "Location" field shows the directory path
4. Combine this with the filename to get the full path
5. Remember to use double backslashes (`\\`) or forward slashes (`/`) in your JSON configuration

## Learning More

To learn more about MCP and how to build more advanced servers:

- Visit the [official MCP documentation](https://modelcontextprotocol.io)
- Explore the [MCP specification](https://github.com/modelcontextprotocol/specification)
- Check out the [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) and [Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Contributing

Feel free to contribute your own examples or improvements to existing ones by submitting a pull request!

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
