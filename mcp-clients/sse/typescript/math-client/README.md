# MCP Math Client with SSE Transport (TypeScript)

This is a TypeScript implementation of a Math Client using the MCP protocol with Server-Sent Events (SSE) transport.

## Features

- MCP Client implementation with SSE transport
- Interactive command-line interface for calling math operations
- Support for add, subtract, multiply, and divide operations
- Error handling for invalid inputs and server communication issues

## Installation

```bash
npm install
```

## Building

```bash
npm run build
```

## Running the Client

To run the client, you need to provide the URL of the MCP server's SSE endpoint:

```bash
npm run dev http://localhost:8000/sse
```

Or with the built version:

```bash
npm start http://localhost:8000/sse
```

## Usage

The client provides an interactive command-line interface where you can:

1. Choose a math operation (add, subtract, multiply, divide)
2. Enter two numbers as parameters
3. See the result returned from the server

## Dependencies

- `@modelcontextprotocol/sdk`: The official MCP TypeScript SDK
- `commander`: For command-line argument parsing
- `eventsource`: For SSE transport
- `readline-sync`: For interactive command-line input
- `zod`: For schema validation
