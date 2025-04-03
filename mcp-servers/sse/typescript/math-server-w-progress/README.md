# MCP Math Server with SSE Transport (TypeScript)

This is a TypeScript implementation of a Math Server using the MCP protocol with Server-Sent Events (SSE) transport.

## Features

- MCP Server implementation with SSE transport
- Math operations: add, subtract, multiply, and divide
- Error handling for invalid operations (like division by zero)

## Installation

```bash
npm install
```

## Building

```bash
npm run build
```

## Running the Server

```bash
npm run dev
```

The server will be available at:
- Server: http://localhost:8000
- SSE Endpoint: http://localhost:8000/sse

## Using with a Client

You can connect to this server using any MCP client that supports SSE transport. The server exposes the following math operations:

- `add(a: number, b: number)`: Add two numbers
- `subtract(a: number, b: number)`: Subtract b from a
- `multiply(a: number, b: number)`: Multiply two numbers
- `divide(a: number, b: number)`: Divide a by b

## Implementation Details

This server is implemented using:
- Express.js for the HTTP server
- @modelcontextprotocol/sdk for the MCP protocol implementation
- Custom SSE transport for server-sent events
- Zod for parameter validation

This is a port of the Python implementation that uses the same functionality but with TypeScript and the official MCP SDK.
