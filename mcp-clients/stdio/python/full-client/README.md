# Personal Knowledge Assistant - MCP Client

This client provides a feature-rich chat interface to interact with the Personal Knowledge Assistant MCP server. It demonstrates a complete implementation of the Model Context Protocol (MCP) client capabilities, handling all aspects:

- **Tools**: Search the web, fetch webpage content, create notes, find notes, generate markdown docs
- **Resources**: Access notes and documents in the knowledge base
- **Prompts**: Use templates for summarization, idea generation, and structured analysis

## Features

- Interactive chat interface with history
- Rich text formatting using the Rich library
- Complete MCP protocol implementation
- Integration with Claude via Anthropic API
- Command system for common operations
- Tool execution visualization
- Resource browsing capabilities
- Prompt template discovery and usage

## Prerequisites

- Python 3.8+
- [Anthropic API key](https://console.anthropic.com/settings/keys)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Run the client by specifying the path to the server script:

```bash
python client.py /path/to/server.py
```

If no path is provided, it will use the default path to the Personal Knowledge Assistant server.

### Available Commands

- `help` - Show help information
- `clear` - Clear the screen
- `exit` - Exit the application
- `list notes` - List all available notes
- `list documents` - List all available documents
- `use prompt <name>` - Use a specific prompt template

### Example Queries

- "Search the web for information about quantum computing"
- "Create a note about the benefits of exercise"
- "Find notes related to machine learning"
- "Generate a markdown document about climate change"

## Architecture

The client follows the MCP client architecture:
1. Connects to the MCP server via STDIO transport
2. Discovers available tools, prompts, and resources
3. Integrates with Claude API for natural language understanding
4. Processes tool calls and manages chat history
5. Presents results in a user-friendly format

## License

MIT

## Credits

Developed as part of the MCP Builder examples project.
