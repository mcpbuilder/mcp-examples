# Personal Knowledge Assistant - Full MCP Server Demo

This project demonstrates a complete MCP (Model Context Protocol) server implementation in Python with tools, resources, and prompts. It showcases how to build a personal knowledge assistant that helps users research topics, manage notes, and generate content.

## Features

This MCP server implements all three core MCP capabilities:

### 1. Tools
- Web research capabilities
  - `search_web`: Search for information on a topic
  - `fetch_webpage_content`: Extract content from a webpage
- Knowledge management
  - `create_note`: Create new notes in the knowledge base
  - `find_notes`: Search for notes by content or tags
- Content generation
  - `generate_markdown_doc`: Create structured markdown documents

### 2. Resources
- Notes access via URIs:
  - `notes:list`: List all notes
  - `notes:id:<id>`: Access a specific note by ID
  - `notes:search:<query>`: Search notes by content
- Documents access:
  - `documents:list`: List all generated documents
  - `documents:id:<id>`: Access a specific document by ID

### 3. Prompts
- `summarize`: Template for summarizing content with customizable length
- `ideastorm`: Generate creative ideas on a topic
- `structured_analysis`: Perform structured analysis of text with different focuses

## Project Structure

```
full-server/
├── server.py            # Main MCP server implementation
├── requirements.txt     # Python dependencies
├── client.json          # MCP client configuration
├── README.md            # This file
└── data/                # Created on first run to store data
    ├── notes/           # Storage for notes
    ├── documents/       # Storage for generated documents
    └── resources/       # Additional resources
```

## Setup and Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make the server executable:
   ```bash
   chmod +x server.py
   ```

3. Configure your MCP client to connect to this server using the provided `client.json`.

## Using with Claude Desktop

To use this server with Claude Desktop:

1. Make sure you have Claude Desktop installed and updated to the latest version
2. Open the Claude Desktop configuration file:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```
3. Add the server configuration (you can copy from the provided client.json)
4. Restart Claude Desktop

## Usage Examples

Here are some examples of how to interact with this MCP server through an AI assistant:

### Research & Content Generation
```
Could you help me research information about renewable energy technologies? 
After finding some information, create a note summarizing the key points.
```

### Using Resources
```
Can you list all my existing notes and then show me the one about machine learning?
```

### Using Prompts
```
I have this article about climate change. Could you use the summarize prompt to create a concise summary?
```

### Full Workflow Example
```
I'm working on a presentation about artificial intelligence ethics. 
Can you search for some recent information, create a structured note with the key points, 
and then generate a markdown document with the main sections I should cover?
```

## Extending the Server

You can extend this server by:

1. Adding new tools by creating additional decorated functions
2. Implementing more resource handlers for different data types
3. Creating additional prompt templates for specific use cases

Refer to the [MCP documentation](https://modelcontextprotocol.io/) for more details on building MCP servers.

## License

This example is provided for educational purposes and is free to use and modify.
