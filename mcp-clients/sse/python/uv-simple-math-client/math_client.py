#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp",
# ]
# ///

import asyncio
import sys
from typing import Optional
from mcp import ClientSession
from mcp.client.sse import sse_client

class SimpleMathClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None

    async def connect_to_server(self, server_url: str):
        """Connect to the math server running with SSE transport"""
        print(f"Connecting to server at {server_url}...")
        
        # Create and store the context managers
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()

        # Initialize the session
        await self.session.initialize()

        # List available tools to verify connection
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

    async def call_math_tool(self, tool_name: str, a: float, b: float):
        """Call a math tool on the server"""
        if not self.session:
            print("Error: Not connected to server")
            return None
        
        try:
            result = await self.session.call_tool(tool_name, {"a": a, "b": b})
            return result.content
        except Exception as e:
            print(f"Error calling {tool_name}: {str(e)}")
            return None

    async def chat_loop(self):
        """Run an interactive chat loop for math operations"""
        print("\nSimple Math Client Started!")
        print("Format: <operation> <number1> <number2>")
        print("Available operations: add, subtract, multiply, divide")
        print("Example: add 5 3")
        print("Type 'quit' to exit.")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() == 'quit':
                    break
                
                parts = command.split()
                if len(parts) != 3:
                    print("Invalid format. Use: <operation> <number1> <number2>")
                    continue
                
                operation, a_str, b_str = parts
                
                try:
                    a = float(a_str)
                    b = float(b_str)
                except ValueError:
                    print("Numbers must be valid integers or floats")
                    continue
                
                if operation not in ['add', 'subtract', 'multiply', 'divide']:
                    print("Unknown operation. Available: add, subtract, multiply, divide")
                    continue
                
                result = await self.call_math_tool(operation, a, b)
                if result is not None:
                    print(f"Result: {result}")
                    
            except Exception as e:
                print(f"Error: {str(e)}")

async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run math_client.py <URL of SSE MCP server>")
        print("Example: uv run math_client.py http://localhost:8000/sse")
        sys.exit(1)

    client = SimpleMathClient()
    try:
        await client.connect_to_server(server_url=sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
