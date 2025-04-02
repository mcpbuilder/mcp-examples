#!/usr/bin/env node

/**
 * Math Client Example using MCP over SSE
 * 
 * This script demonstrates a simple MCP client that connects to a math server using SSE and calls math tools.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { createInterface } from 'readline/promises';
import { URL } from 'url';
import {
  CallToolResult
} from "@modelcontextprotocol/sdk/types.js";

// Get server URL from command line argument
const serverUrl = process.argv[2];
if (!serverUrl) {
  console.error("Please provide the server URL as a command line argument");
  console.error("Example: npm run dev http://localhost:8000/sse");
  process.exit(1);
}

async function main() {
  const url = new URL(serverUrl);
  const transport = new SSEClientTransport(url);
  
  // Create MCP client
  const client = new Client({ name: "Math Client", version: "1.0.0" });
  
  try {
    // Connect to the server
    console.log(`Connecting to math server at ${serverUrl}...`);
    await client.connect(transport);
    console.log("Connected successfully!");
    
    // Get server information
    const serverInfo = client.getServerVersion();
    console.log(`Connected to: ${serverInfo?.name} v${serverInfo?.version}`);
    
    // List available tools
    const tools = await client.listTools();
    console.log("Available tools:");
    tools.tools.forEach(tool => {
      console.log(`- ${tool.name}: ${tool.description}`);
    });
    
    // Setup readline interface for user input
    const readline = createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    console.log("\nMath Client Ready. Type 'exit' to quit.");
    console.log("Example: add 5 3");
    
    while (true) {
      const input = await readline.question("\nEnter operation (add/subtract/multiply/divide) and numbers: ");
      
      if (input.toLowerCase() === 'exit') {
        break;
      }
      
      const parts = input.trim().split(/\s+/);
      if (parts.length < 3) {
        console.log("Invalid input. Please use format: operation number1 number2");
        continue;
      }
      
      const operation = parts[0].toLowerCase();
      const num1 = parseFloat(parts[1]);
      const num2 = parseFloat(parts[2]);
      
      if (isNaN(num1) || isNaN(num2)) {
        console.log("Invalid numbers. Please enter valid numbers.");
        continue;
      }

      console.log(`Calling ${operation} with ${num1} and ${num2}`);
      
      try {
        const result = await client.callTool({
          name: operation,
          arguments: { a: num1, b: num2 }
        }) as CallToolResult;

        console.log(`Result: ${result.content?.[0]?.text}`);
      } catch (error) {
        console.error(`Error calling ${operation}:`, error);
      }
    }
    
    readline.close();
    
  } catch (error) {
    console.error("Error:", error);
  } finally {
    // Close the client connection
    await client.close();
    console.log("Connection closed");
  }
}

main().catch(error => {
  console.error("Unhandled error:", error);
  process.exit(1);
});