# TypeScript MCP Server Example

This example demonstrates how to create a simple Model Context Protocol (MCP) server using TypeScript. This is perfect for beginners who want to get started with MCP in a JavaScript/TypeScript environment.

## This Example

This example implements a simple MCP server that provides:

- An "echo" tool that returns the input message
- An "echo" resource that demonstrates resource handling
- An "echo" prompt template for consistent message formatting
- Uses the official MCP TypeScript SDK

## Prerequisites

- Node.js (latest LTS recommended)
- npm or another package manager

## Getting Started

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Build the project**

   ```bash
   npm run build
   ```

3. **Configure your MCP client**

   Update the `client.json` file with the correct path for your system:

   ```json
   {
       "mcpServers": {
           "echo": {
               "command": "node",
               "args": [
                   "/path/to/built/javascript/file/mcp-server.js"
               ]
           }
       }
   }
   ```

   Replace `/path/to/built/javascript/file/mcp-server.js` with the actual path to your built JavaScript file (typically in the `build` directory).

   ### Finding the Correct Paths

   #### For macOS/Linux:
   
   1. After building the project, find the full path to the built JavaScript file:
      ```bash
      cd /path/to/mcp-examples/typescript/simple-server
      pwd
      ```
      Then add `/build/mcp-server.js` to this path.
      
   2. Your final path might look like:
      ```
      /Users/username/projects/mcp-examples/typescript/simple-server/build/mcp-server.js
      ```
      
   #### For Windows:
   
   1. Navigate to the build folder in File Explorer
   2. Right-click on `mcp-server.js` and select "Properties"
   3. Copy the location and filename
   4. Use the path with double backslashes or forward slashes
      
   Example Windows configuration:
   
   ```json
   {
       "mcpServers": {
           "echo": {
               "command": "node",
               "args": [
                   "C:\\Path\\To\\mcp-examples\\typescript\\simple-server\\build\\mcp-server.js"
               ]
           }
       }
   }
   ```
   
   Note: On Windows, you don't need to specify the full path to `node` as long as it's in your system PATH.

4. **Connect with an MCP client**

   You can now use any MCP-compatible client (like Claude for Desktop) to interact with your server. The server will appear as an "echo" server with echo capabilities.

## Understanding the Code

The server implements three key MCP features:

### 1. Resources

```typescript
server.resource(
  "echo",
  new ResourceTemplate("echo://{message}", { list: undefined }),
  async (uri, { message }) => ({
    contents: [{
      uri: uri.href,
      text: `Resource echo: ${message}`
    }]
  })
);
```

This creates a resource that can be accessed with a URI like `echo://hello`, which returns the message.

### 2. Tools

```typescript
server.tool(
  "echo",
  { message: z.string() },
  async ({ message }) => ({
    content: [{ type: "text", text: `Tool echo: ${message}` }]
  })
);
```

This creates a tool that can be called with a message parameter and returns that message.

### 3. Prompts

```typescript
server.prompt(
  "echo",
  { message: z.string() },
  ({ message }) => ({
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: `Please process this message: ${message}`
      }
    }]
  })
);
```

This creates a prompt template that formats messages consistently.

## Project Structure

- `mcp-server.ts` - The main server implementation
- `client.json` - Configuration for MCP clients
- `package.json` - Node.js dependencies and build scripts
- `tsconfig.json` - TypeScript configuration
- `build/` - Output directory for compiled JavaScript

## Next Steps

Once you're comfortable with this example, you can:

1. Add more complex tools to your server
2. Implement more sophisticated resources
3. Create advanced prompt templates
4. Check out the [MCP documentation](https://modelcontextprotocol.io) for advanced topics

## Troubleshooting

If your MCP client isn't connecting to your server:

1. Verify the paths in your `client.json` file
2. Make sure the server is built correctly (`npm run build`)
3. Check that Node.js is installed and accessible
4. Ensure all dependencies are installed correctly

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Client Examples](https://modelcontextprotocol.io/clients)
