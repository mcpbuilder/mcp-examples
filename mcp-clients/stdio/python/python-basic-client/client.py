"""
Basic MCP Client Example

This script demonstrates a simple MCP client implementation that can:
1. Connect to an MCP server
2. Discover available tools
3. Process queries using Claude
4. Execute tool calls and handle results
"""

import asyncio
import argparse
import sys
import os
from typing import Optional, Dict, Any, List
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
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not found in environment variables.")
            print("Please create a .env file with your API key or set it in your environment.")
            sys.exit(1)
            
        self.anthropic = Anthropic(api_key=api_key)
        
    async def connect_to_server(self, server_script_path: str) -> bool:
        """Connect to an MCP server.
        
        Args:
            server_script_path: Path to the server script (.py or .js)
            
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Determine the command based on file extension
            is_python = server_script_path.endswith('.py')
            is_js = server_script_path.endswith('.js')
            
            if not (is_python or is_js):
                print(f"Error: Server script must be a .py or .js file. Got: {server_script_path}")
                return False
                
            command = "python" if is_python else "node"
            
            # Set up server parameters
            server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],
                env=None
            )
            
            # Connect to the server
            print(f"Connecting to MCP server: {server_script_path}")
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
            
            # Initialize the session
            await self.session.initialize()
            
            # List available tools
            response = await self.session.list_tools()
            tools = response.tools
            
            if not tools:
                print("Warning: No tools available from this server.")
            else:
                print("\nConnected to server with tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                    
            return True
            
        except Exception as e:
            print(f"Error connecting to server: {str(e)}")
            return False
            
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools.
        
        Args:
            query: The user's query
            
        Returns:
            str: The final response
        """
        if not self.session:
            return "Error: Not connected to an MCP server. Please connect first."
            
        # Prepare the initial message
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        # Get available tools from the server
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
        
        if not available_tools:
            print("Warning: No tools available from the server.")
            
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
                
                # Execute tool call
                print(f"\nClaude is calling tool: {tool_name}")
                print(f"With arguments: {tool_args}")
                
                try:
                    result = await self.session.call_tool(tool_name, tool_args)
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
        """Close the connection to the MCP server."""
        await self.exit_stack.aclose()
        print("\nDisconnected from MCP server.")

async def main():
    """Main entry point for the MCP client."""
    parser = argparse.ArgumentParser(description="Basic MCP Client Example")
    parser.add_argument("server_path", help="Path to the MCP server script (.py or .js)")
    parser.add_argument("--query", help="Query to process (if not provided, will use an example query)")
    
    args = parser.parse_args()
    
    client = MCPClient()
    
    try:
        # Connect to the server
        connected = await client.connect_to_server(args.server_path)
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
