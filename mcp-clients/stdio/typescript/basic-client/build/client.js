#!/usr/bin/env node
/**
 * Basic MCP Client Example
 *
 * This script demonstrates a simple MCP client implementation that can:
 * 1. Connect to MCP servers defined in a configuration file
 * 2. Discover available tools
 * 3. Process queries using Claude
 * 4. Execute tool calls and handle results
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { Anthropic } from "@anthropic-ai/sdk";
import { readFile } from 'fs/promises';
import { createInterface } from 'readline/promises';
import dotenv from 'dotenv';
import path from 'path';
// Load environment variables from .env file
dotenv.config();
// Check for required environment variables
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
if (!ANTHROPIC_API_KEY) {
    console.error("Error: ANTHROPIC_API_KEY is not set");
    console.error("Please create a .env file with your API key or set it in your environment.");
    process.exit(1);
}
class MCPClient {
    mcp;
    anthropic;
    sessions = new Map();
    constructor() {
        this.anthropic = new Anthropic({
            apiKey: ANTHROPIC_API_KEY,
        });
        this.mcp = new Client({ name: "typescript-mcp-client", version: "1.0.0" });
    }
    /**
     * Load MCP server configuration from a JSON file
     * @param configPath Path to the JSON configuration file
     * @returns ClientConfig object
     */
    async loadConfig(configPath) {
        try {
            const configData = await readFile(configPath, 'utf8');
            return JSON.parse(configData);
        }
        catch (error) {
            console.error(`Error loading configuration file: ${error}`);
            process.exit(1);
        }
    }
    /**
     * Connect to all MCP servers defined in the configuration file
     * @param configPath Path to the JSON configuration file
     * @returns true if at least one connection was successful, false otherwise
     */
    async connectToServers(configPath) {
        try {
            // Load the configuration
            const config = await this.loadConfig(configPath);
            // Check if there are any servers in the config
            if (!config.mcpServers || Object.keys(config.mcpServers).length === 0) {
                console.error("Error: No MCP servers found in configuration.");
                return false;
            }
            // Connect to each server in the configuration
            let success = false;
            for (const [serverName, serverConfig] of Object.entries(config.mcpServers)) {
                try {
                    // Replace ${PWD} with current working directory if present
                    const command = serverConfig.command.replace('${PWD}', process.cwd());
                    // Connect to the server
                    console.log(`Connecting to MCP server: ${serverName}`);
                    const transport = new StdioClientTransport({
                        command,
                        args: serverConfig.args,
                        env: serverConfig.env,
                    });
                    await transport.connect();
                    await this.mcp.connect(transport);
                    // List available tools
                    const tools = await this.mcp.listTools();
                    if (!tools || tools.length === 0) {
                        console.warn(`Warning: No tools available from server '${serverName}'.`);
                    }
                    else {
                        console.log(`\nConnected to server '${serverName}' with tools:`);
                        for (const tool of tools) {
                            console.log(`  - ${tool.name}: ${tool.description}`);
                        }
                    }
                    // Store the session
                    this.sessions.set(serverName, {
                        transport,
                        tools: tools.map(tool => ({
                            name: tool.name,
                            description: tool.description,
                            input_schema: tool.inputSchema
                        }))
                    });
                    success = true;
                }
                catch (error) {
                    console.error(`Error connecting to server '${serverName}': ${error}`);
                }
            }
            return success;
        }
        catch (error) {
            console.error(`Error connecting to servers: ${error}`);
            return false;
        }
    }
    /**
     * Process a query using Claude and available tools
     * @param query The user's query
     * @returns The final response
     */
    async processQuery(query) {
        if (this.sessions.size === 0) {
            return "Error: Not connected to any MCP servers. Please connect first.";
        }
        // Prepare the initial message
        const messages = [
            {
                role: "user",
                content: query
            }
        ];
        // Get available tools from all servers
        const availableTools = [];
        for (const [serverName, session] of this.sessions.entries()) {
            availableTools.push(...session.tools);
        }
        if (availableTools.length === 0) {
            console.warn("Warning: No tools available from any server.");
        }
        // Make initial call to Claude
        console.log("\nSending query to Claude...");
        let response = await this.anthropic.messages.create({
            model: "claude-3-sonnet-20240229", // Use a more widely available model
            max_tokens: 1000,
            messages,
            tools: availableTools
        });
        // Process response and handle tool calls
        const finalText = [];
        // Process the initial response
        let assistantMessageContent = [];
        for (const content of response.content) {
            if (content.type === 'text') {
                finalText.push(content.text);
                assistantMessageContent.push(content);
            }
            else if (content.type === 'tool_use') {
                const toolName = content.name;
                const toolArgs = content.input;
                // Execute tool call on the appropriate server
                console.log(`\nClaude is calling tool: ${toolName}`);
                console.log(`With arguments: ${JSON.stringify(toolArgs)}`);
                try {
                    // Find a session that has this tool
                    let serverWithTool = null;
                    for (const [serverName, session] of this.sessions.entries()) {
                        if (session.tools.some(tool => tool.name === toolName)) {
                            serverWithTool = serverName;
                            break;
                        }
                    }
                    if (!serverWithTool) {
                        throw new Error(`No server found with tool: ${toolName}`);
                    }
                    // Call the tool
                    const result = await this.mcp.callTool(toolName, toolArgs);
                    console.log(`Tool result: ${JSON.stringify(result.content)}`);
                    // Add the assistant's message with the tool call
                    assistantMessageContent.push(content);
                    messages.push({
                        role: "assistant",
                        content: assistantMessageContent
                    });
                    // Add the tool result as a user message
                    messages.push({
                        role: "user",
                        content: [
                            {
                                type: "tool_result",
                                tool_use_id: content.id,
                                content: result.content
                            }
                        ]
                    });
                    // Get next response from Claude
                    console.log("\nSending tool result back to Claude...");
                    response = await this.anthropic.messages.create({
                        model: "claude-3-sonnet-20240229",
                        max_tokens: 1000,
                        messages,
                        tools: availableTools
                    });
                    // Add the new response text
                    assistantMessageContent = [];
                    for (const content of response.content) {
                        if (content.type === 'text') {
                            finalText.push(content.text);
                            assistantMessageContent.push(content);
                        }
                    }
                }
                catch (error) {
                    const errorMessage = `Error executing tool ${toolName}: ${error}`;
                    console.error(errorMessage);
                    finalText.push(`\n${errorMessage}`);
                }
            }
        }
        return finalText.join("\n");
    }
    /**
     * Disconnect from all MCP servers
     */
    async disconnect() {
        for (const [serverName, session] of this.sessions.entries()) {
            try {
                await session.transport.disconnect();
                console.log(`Disconnected from server: ${serverName}`);
            }
            catch (error) {
                console.error(`Error disconnecting from server '${serverName}': ${error}`);
            }
        }
        this.sessions.clear();
    }
}
/**
 * Main entry point for the MCP client
 */
async function main() {
    // Parse command line arguments
    const args = process.argv.slice(2);
    let configPath = path.join(process.cwd(), 'client.json');
    let query = null;
    // Process arguments
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--config' && i + 1 < args.length) {
            configPath = args[i + 1];
            i++;
        }
        else if (args[i] === '--query' && i + 1 < args.length) {
            query = args[i + 1];
            i++;
        }
        else if (!configPath && args[i].endsWith('.json')) {
            configPath = args[i];
        }
        else if (!query && i === args.length - 1) {
            query = args[i];
        }
    }
    // Create and initialize the MCP client
    const client = new MCPClient();
    try {
        // Connect to MCP servers
        const success = await client.connectToServers(configPath);
        if (!success) {
            console.error("Failed to connect to any MCP servers. Exiting.");
            process.exit(1);
        }
        // Process query if provided, otherwise use interactive prompt
        if (query) {
            const response = await client.processQuery(query);
            console.log("\nFinal response:");
            console.log(response);
        }
        else {
            console.log("\nNo query provided. Using an interactive prompt.");
            const rl = createInterface({
                input: process.stdin,
                output: process.stdout
            });
            while (true) {
                const userQuery = await rl.question("Enter your query (or type 'exit' to quit): ");
                if (userQuery.toLowerCase() === 'exit') {
                    break;
                }
                const response = await client.processQuery(userQuery);
                console.log("\nFinal response:");
                console.log(response);
            }
            rl.close();
        }
        // Disconnect from all servers
        await client.disconnect();
    }
    catch (error) {
        console.error(`Fatal error: ${error}`);
        process.exit(1);
    }
}
// Run the main function
main().catch(error => {
    console.error("Fatal error in main():", error);
    process.exit(1);
});
