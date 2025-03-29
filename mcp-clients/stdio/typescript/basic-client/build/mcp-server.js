#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
// Create an MCP server
const server = new McpServer({
    name: "Math",
    version: "1.0.0"
});
// Add a tool for addition
server.tool("add", { a: z.number(), b: z.number() }, async ({ a, b }) => ({
    content: [{
            type: "text",
            text: `${a + b}`
        }]
}));
// Add a tool for subtraction
server.tool("subtract", { a: z.number(), b: z.number() }, async ({ a, b }) => ({
    content: [{
            type: "text",
            text: `${a - b}`
        }]
}));
// Add a tool for multiplication
server.tool("multiply", { a: z.number(), b: z.number() }, async ({ a, b }) => ({
    content: [{
            type: "text",
            text: `${a * b}`
        }]
}));
// Add a tool for division
server.tool("divide", { a: z.number(), b: z.number() }, async ({ a, b }) => {
    if (b === 0) {
        throw new Error("Cannot divide by zero");
    }
    return {
        content: [{
                type: "text",
                text: `${a / b}`
            }]
    };
});
// Add a simple echo tool
server.tool("echo", { message: z.string() }, async ({ message }) => ({
    content: [{
            type: "text",
            text: `Echo: ${message}`
        }]
}));
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Math MCP Server running on stdio");
}
main().catch((error) => {
    console.error("Fatal error in main():", error);
    process.exit(1);
});
