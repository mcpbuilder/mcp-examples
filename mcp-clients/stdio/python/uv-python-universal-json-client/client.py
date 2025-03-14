# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp",
#     "anthropic",
#     "dotenv"
# ]
# ///

"""
Basic MCP Client Example

This script demonstrates a simple MCP client implementation that can:
1. Connect to MCP servers defined in a configuration file
2. Discover available tools
3. Process queries using Claude
4. Execute tool calls and handle results
"""

import asyncio
import argparse
import sys
import os
import json
from typing import Optional, Dict, Any, List, Tuple
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class MCPClient:
    """A basic MCP client implementation."""
    
    def __init__(self):
        """Initialize the MCP client."""
        self.sessions = {}  # Dictionary to store sessions for each server
        self.exit_stack = AsyncExitStack()
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not found in environment variables.")
            print("Please create a .env file with your API key or set it in your environment.")
            sys.exit(1)
            
        self.anthropic = Anthropic(api_key=api_key)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load MCP server configuration from a JSON file.
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            Dict containing the MCP server configuration
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Error loading configuration file: {str(e)}")
            sys.exit(1)
        
    async def connect_to_servers(self, config_path: str) -> bool:
        """Connect to all MCP servers defined in the configuration file.
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            bool: True if at least one connection was successful, False otherwise
        """
        try:
            # Load the configuration
            config = self.load_config(config_path)
            
            # Check if there are any servers in the config
            if 'mcpServers' not in config or not config['mcpServers']:
                print("Error: No MCP servers found in configuration.")
                return False
            
            # Connect to each server in the configuration
            success = False
            for server_name, server_config in config['mcpServers'].items():
                try:
                    # Set up server parameters
                    server_params = StdioServerParameters(
                        command=server_config.get('command', ''),
                        args=server_config.get('args', []),
                        env=server_config.get('env', {})
                    )
                    
                    # Connect to the server
                    print(f"Connecting to MCP server: {server_name}")
                    stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                    stdio, write = stdio_transport
                    session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
                    
                    # Initialize the session
                    await session.initialize()
                    
                    # Store the session
                    self.sessions[server_name] = session
                    
                    # List available tools
                    response = await session.list_tools()
                    tools = response.tools
                    
                    if not tools:
                        print(f"Warning: No tools available from server '{server_name}'.")
                    else:
                        print(f"\nConnected to server '{server_name}' with tools:")
                        for tool in tools:
                            print(f"  - {tool.name}: {tool.description}")
                    
                    success = True
                except Exception as e:
                    print(f"Error connecting to server '{server_name}': {str(e)}")
            
            return success
            
        except Exception as e:
            print(f"Error connecting to servers: {str(e)}")
            return False
            
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools.
        
        Args:
            query: The user's query
            
        Returns:
            str: The final response
        """
        if not self.sessions:
            return "Error: Not connected to any MCP servers. Please connect first."
            
        # Prepare the initial message
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        # Get available tools from all servers
        available_tools = []
        for server_name, session in self.sessions.items():
            response = await session.list_tools()
            server_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]
            available_tools.extend(server_tools)
        
        if not available_tools:
            print("Warning: No tools available from any server.")
            
        # Make initial call to Claude
        print("\nSending query to Claude...")
        response = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",  # Use a more widely available model
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )
        
        # Process response and handle tool calls
        final_text = []
        
        # Process the initial response
        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call on the appropriate server
                print(f"\nClaude is calling tool: {tool_name}")
                print(f"With arguments: {tool_args}")
                
                try:
                    # Find a session that has this tool
                    session_with_tool = None
                    for server_name, session in self.sessions.items():
                        response = await session.list_tools()
                        if any(tool.name == tool_name for tool in response.tools):
                            session_with_tool = session
                            break
                    
                    if not session_with_tool:
                        raise Exception(f"No server found with tool '{tool_name}'")
                    
                    result = await session_with_tool.call_tool(tool_name, tool_args)
                    print(f"Tool result: {result.content}")
                    
                    # Add the assistant's message with the tool call
                    assistant_message_content.append(content)
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message_content
                    })
                    
                    # Add the tool result as a user message
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result.content
                            }
                        ]
                    })
                    
                    # Get next response from Claude
                    print("\nSending tool result back to Claude...")
                    response = self.anthropic.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1000,
                        messages=messages,
                        tools=available_tools
                    )
                    
                    # Add the new response text
                    for content in response.content:
                        if content.type == 'text':
                            final_text.append(content.text)
                            
                except Exception as e:
                    error_message = f"Error executing tool {tool_name}: {str(e)}"
                    print(error_message)
                    final_text.append(error_message)
        
        # Join all the text parts
        return "\n".join(final_text)
        
    async def close(self):
        """Close the connection to all MCP servers."""
        await self.exit_stack.aclose()
        print("\nDisconnected from all MCP servers.")

async def main():
    """Main entry point for the MCP client."""
    parser = argparse.ArgumentParser(description="Basic MCP Client Example")
    parser.add_argument("--config", help="Path to the MCP configuration JSON file", default="mcp-config.json")
    parser.add_argument("--query", help="Query to process (if not provided, will use an interactive prompt)")
    
    args = parser.parse_args()
    
    client = MCPClient()
    
    try:
        # Connect to all servers using the configuration
        connected = await client.connect_to_servers(args.config)
        if not connected:
            return
            
        # Process a query
        query = args.query
        if not query:
            print("\nNo query provided. Using an interactive prompt.")
            print("Enter your query (or type 'exit' to quit):")
            query = input("> ")
            
            while query.lower() != 'exit':
                if query:
                    result = await client.process_query(query)
                    print("\nResult:")
                    print(result)
                    
                print("\nEnter another query (or type 'exit' to quit):")
                query = input("> ")
        else:
            # Process the provided query
            result = await client.process_query(query)
            print("\nResult:")
            print(result)
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the connection
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
