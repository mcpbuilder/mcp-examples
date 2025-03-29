#!/usr/bin/env python3
"""
Personal Knowledge Assistant - MCP Client

This client provides a chat interface to interact with the Personal Knowledge Assistant
MCP server. It handles all aspects of the MCP protocol: tools, resources, and prompts.
"""

import os
import sys
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from contextlib import AsyncExitStack
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

from anthropic import Anthropic
from anthropic.types import ContentBlockParam, ToolUseBlockParam, TextBlockParam, ToolResultBlockParam, MessageParam

# Set up logging to file only
log_file = "/tmp/mcp_client.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("mcp_client")

# Disable Anthropic's debug logs
logging.getLogger("anthropic").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("markdown_it").setLevel(logging.WARNING)

# Initialize console for rich output
console = Console()

# Load environment variables
load_dotenv()

# Anthropic API key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    console.print("[bold red]Error:[/bold red] ANTHROPIC_API_KEY not found in environment variables")
    console.print("Please set your Anthropic API key in a .env file or environment variables")
    sys.exit(1)

# Constants
MODEL = os.getenv("ANTHROPIC_MODEL")
DEFAULT_SERVER_PATH = "../../../mcp-servers/stdio/python/full-server/server.py"
HISTORY_FILE = os.path.expanduser("~/.pka_client_history")

# Tool display configurations
TOOL_ICONS = {
    "search_web": "🔍",
    "fetch_webpage_content": "📄",
    "create_note": "📝",
    "find_notes": "🔎",
    "generate_markdown_doc": "📑",
    "add": "➕",
    "echo": "🔊",
    "get_resource_roots": "📂",
    "read_resource": "📚"
}

# Custom prompt styles
prompt_style = Style.from_dict({
    'prompt': 'ansicyan bold',
})

# Custom key bindings
kb = KeyBindings()
@kb.add('c-c')
def _(event):
    """Exit when Control-C is pressed."""
    event.app.exit()


class PersonalKnowledgeAssistantClient:
    """Client for interacting with the Personal Knowledge Assistant MCP server."""
    
    def __init__(self, server_path: str = DEFAULT_SERVER_PATH):
        """Initialize the client.
        
        Args:
            server_path: Path to the MCP server script
        """
        self.server_path = os.path.abspath(server_path)
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.prompt_session = PromptSession(
            history=FileHistory(HISTORY_FILE),
            style=prompt_style,
            key_bindings=kb
        )
        self.available_tools = []
        self.available_prompts = []
        self.resource_roots = []
        self.chat_history: List[MessageParam] = []
        
    async def connect_to_server(self) -> None:
        """Connect to the MCP server."""
        try:
            with console.status("[bold green]Connecting to server...[/bold green]"):
                # Determine if server is Python or JS
                is_python = self.server_path.endswith('.py')
                command = "python" if is_python else "node"
                
                # Set up server parameters
                server_params = StdioServerParameters(
                    command=command,
                    args=[self.server_path],
                    env=None
                )
                
                # Create transport and session
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                self.stdio, self.write = stdio_transport
                self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
                
                # Initialize session
                await self.session.initialize()
                
                # Get available tools
                tools_response = await self.session.list_tools()
                self.available_tools = tools_response.tools
                
                # Get available prompts
                prompts_response = await self.session.list_prompts()
                self.available_prompts = prompts_response.prompts
                
                # Get resource roots
                try:
                    # Try calling get_resource_roots as a tool
                    logger.debug("Calling get_resource_roots tool")
                    roots_response = await self.session.call_tool("get_resource_roots", {})
                    logger.debug(f"Received response from get_resource_roots: {roots_response}")
                    
                    # Extract content from CallToolResult
                    if hasattr(roots_response, 'content') and isinstance(roots_response.content, list):
                        for content_item in roots_response.content:
                            if hasattr(content_item, 'text'):
                                try:
                                    # Parse the JSON response
                                    logger.debug(f"Parsing content text: {content_item.text}")
                                    result = json.loads(content_item.text)
                                    if isinstance(result, dict) and "roots" in result:
                                        self.resource_roots = result["roots"]
                                        logger.debug(f"Found resource roots: {self.resource_roots}")
                                        break
                                except json.JSONDecodeError as e:
                                    logger.error(f"Failed to parse JSON: {e}")
                    else:
                        logger.warning("No content found in response")
                        self.resource_roots = []
                except Exception as e:
                    # If tool call fails, set empty resource roots
                    logger.error(f"Error calling get_resource_roots: {e}")
                    self.resource_roots = []
                
            # Display connected server information
            console.print(Panel.fit(
                f"[bold green]Connected to Personal Knowledge Assistant[/bold green]\n"
                f"[bold]Available Tools:[/bold] {', '.join(tool.name for tool in self.available_tools)}\n"
                f"[bold]Available Prompts:[/bold] {', '.join(prompt.name for prompt in self.available_prompts)}\n"
                f"[bold]Resource Roots:[/bold] {', '.join(root for root in self.resource_roots)}",
                title="🔌 Connection Successful",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[bold red]Error connecting to server:[/bold red] {str(e)}")
            await self.exit_stack.aclose()
            sys.exit(1)
    
    async def process_query(self, query: str) -> None:
        """Process a user query using Claude and MCP capabilities.
        
        Args:
            query: The user's query
        """
        # Format tools for Anthropic API
        anthropic_tools = self.get_anthropic_tools()
        
        # Add query to chat history
        self.chat_history.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query
                }
            ]
        })
        
        # Initial API call to Claude
        try:
            with console.status("[bold blue]Thinking...[/bold blue]"):
                response = self.anthropic.messages.create(
                    model=MODEL,
                    max_tokens=4000,
                    messages=self.chat_history,
                    tools=anthropic_tools
                )
            
            # Process and display response
            assistant_message_content = []
            
            for content in response.content:
                # Handle text content
                if content.type == "text":
                    assistant_message_content.append(content)
                    console.print(Panel(
                        Markdown(content.text),
                        title="Claude",
                        border_style="green"
                    ))
                elif content.type == "tool_use":
                    # Handle tool use request
                    tool_name = content.name
                    tool_args = content.input
                    tool_id = content.id
                    
                    console.print(f"[bold cyan]Claude wants to use tool:[/bold cyan] {tool_name}")
                    console.print(f"[cyan]Arguments:[/cyan] {json.dumps(tool_args, indent=2)}")
                    
                    # Execute the tool
                    try:
                        tool_result = await self.execute_tool(tool_name, tool_args)
                        
                        # Add tool use to chat history
                        self.chat_history.append({
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": tool_id,
                                    "name": tool_name,
                                    "input": tool_args
                                }
                            ]
                        })
                        
                        # Add tool result to chat history
                        self.chat_history.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,
                                    "content": tool_result
                                }
                            ]
                        })
                        
                        # Get follow-up response from Claude
                        with console.status("[bold blue]Processing results...[/bold blue]"):
                            follow_up_response = self.anthropic.messages.create(
                                model=MODEL,
                                max_tokens=4000,
                                messages=self.chat_history,
                                tools=anthropic_tools
                            )
                            
                            # Display follow-up response
                            for content in follow_up_response.content:
                                if content.type == "text":
                                    console.print(Panel(
                                        Markdown(content.text),
                                        title="Claude",
                                        border_style="green"
                                    ))
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name}: {str(e)}")
                        console.print(f"[bold red]Error executing tool:[/bold red] {str(e)}")
            
            # Add assistant response to chat history
            self.chat_history.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content.text
                    } for content in assistant_message_content if hasattr(content, 'text')
                ]
            })
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    def get_anthropic_tools(self):
        """Format available tools for the Anthropic API."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in self.available_tools
        ]
    
    async def execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """Execute a tool requested by Claude.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Tool execution result as a string
        """
        logger.info(f"Executing tool: {tool_name} with args: {json.dumps(tool_args)}")
        
        try:
            # Find the matching tool
            matching_tool = next((tool for tool in self.available_tools if tool.name == tool_name), None)
            
            if not matching_tool:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # Execute the tool
            if self.session:
                # Convert arguments to the format expected by the tool
                converted_args = {}
                
                # Get the input schema to determine parameter types
                if matching_tool.inputSchema and "properties" in matching_tool.inputSchema:
                    properties = matching_tool.inputSchema.get("properties", {})
                    
                    for arg_name, arg_value in tool_args.items():
                        if arg_name in properties:
                            prop_type = properties[arg_name].get("type", "string")
                            
                            # Convert the value based on the expected type
                            if prop_type == "integer" and not isinstance(arg_value, int):
                                try:
                                    converted_args[arg_name] = int(arg_value)
                                except (ValueError, TypeError):
                                    logger.warning(f"Could not convert {arg_name}={arg_value} to integer")
                                    converted_args[arg_name] = arg_value
                            elif prop_type == "number" and not isinstance(arg_value, (int, float)):
                                try:
                                    converted_args[arg_name] = float(arg_value)
                                except (ValueError, TypeError):
                                    logger.warning(f"Could not convert {arg_name}={arg_value} to number")
                                    converted_args[arg_name] = arg_value
                            elif prop_type == "boolean" and not isinstance(arg_value, bool):
                                if isinstance(arg_value, str):
                                    converted_args[arg_name] = arg_value.lower() in ("true", "yes", "1")
                                else:
                                    converted_args[arg_name] = bool(arg_value)
                            else:
                                converted_args[arg_name] = arg_value
                        else:
                            # If the property is not in the schema, pass it as-is
                            converted_args[arg_name] = arg_value
                else:
                    # If no schema is available, use the arguments as-is
                    converted_args = tool_args
                
                logger.info(f"Converted arguments: {json.dumps(converted_args)}")
                
                # Execute the tool with the converted arguments
                with console.status(f"[bold blue]Executing {tool_name}...[/bold blue]"):
                    tool_result = await self.session.call_tool(tool_name, converted_args)
                
                # Format the result
                if hasattr(tool_result, 'content') and tool_result.content:
                    result_text = ""
                    result_data = None
                    
                    for content_item in tool_result.content:
                        if hasattr(content_item, 'text'):
                            result_text += content_item.text
                        elif hasattr(content_item, 'data'):
                            try:
                                if isinstance(content_item.data, str):
                                    result_text += content_item.data
                                else:
                                    result_data = content_item.data
                                    result_text += json.dumps(content_item.data, indent=2)
                            except:
                                result_text += str(content_item.data)
                    
                    # Display the tool result in a panel
                    tool_icon = TOOL_ICONS.get(tool_name, "🔧")
                    
                    # Determine if result is JSON and format accordingly
                    if result_data or (result_text.strip().startswith('{') and result_text.strip().endswith('}')):
                        try:
                            if not result_data:
                                result_data = json.loads(result_text)
                            # Display as syntax-highlighted JSON
                            console.print(Panel(
                                Syntax(json.dumps(result_data, indent=2), "json", theme="monokai"),
                                title=f"{tool_icon} {tool_name} Result",
                                border_style="cyan"
                            ))
                        except json.JSONDecodeError:
                            # If not valid JSON, display as plain text
                            console.print(Panel(
                                result_text,
                                title=f"{tool_icon} {tool_name} Result",
                                border_style="cyan"
                            ))
                    else:
                        # Display as plain text or markdown if it looks like markdown
                        if '##' in result_text or '*' in result_text:
                            console.print(Panel(
                                Markdown(result_text),
                                title=f"{tool_icon} {tool_name} Result",
                                border_style="cyan"
                            ))
                        else:
                            console.print(Panel(
                                result_text,
                                title=f"{tool_icon} {tool_name} Result",
                                border_style="cyan"
                            ))
                    
                    return result_text
                else:
                    console.print(Panel(
                        "Tool executed successfully, but returned no content",
                        title=f"{TOOL_ICONS.get(tool_name, '🔧')} {tool_name} Result",
                        border_style="cyan"
                    ))
                    return "Tool executed successfully, but returned no content"
            else:
                raise RuntimeError("Not connected to server")
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            console.print(Panel(
                f"[bold red]{error_msg}[/bold red]",
                title=f"❌ {tool_name} Error",
                border_style="red"
            ))
            return f"Error: {error_msg}"
    
    async def handle_resource_commands(self, query: str) -> bool:
        """Handle resource-specific commands.
        
        Args:
            query: The user query
            
        Returns:
            True if command was handled, False otherwise
        """
        # Check for resource listing command
        if query.strip().lower() in ["list notes", "list all notes"]:
            with console.status("[bold cyan]Fetching notes...[/bold cyan]"):
                response = await self.session.read_resource("notes:list")
                data = json.loads(response.content[0].data)
                
            if data:
                console.print(Panel(
                    "\n".join(f"📝 [bold]{note['title']}[/bold] ({note['id']})" for note in data),
                    title="📚 Available Notes",
                    border_style="cyan"
                ))
            else:
                console.print("[yellow]No notes found in the knowledge base[/yellow]")
            return True
            
        elif query.strip().lower() in ["list docs", "list documents", "list all documents"]:
            with console.status("[bold cyan]Fetching documents...[/bold cyan]"):
                response = await self.session.read_resource("documents:list")
                data = json.loads(response.content[0].data)
                
            if data:
                console.print(Panel(
                    "\n".join(f"📄 [bold]{doc['title']}[/bold] ({doc['id']})" for doc in data),
                    title="📚 Available Documents",
                    border_style="cyan"
                ))
            else:
                console.print("[yellow]No documents found in the knowledge base[/yellow]")
            return True
            
        # Check for prompt commands
        elif query.strip().lower().startswith("use prompt "):
            prompt_name = query.strip()[11:].strip()
            valid_prompts = [p.name for p in self.available_prompts]
            
            if prompt_name in valid_prompts:
                console.print(f"[cyan]Using prompt template: [bold]{prompt_name}[/bold][/cyan]")
                console.print("Enter parameters (leave blank for defaults):")
                
                # Find the prompt
                prompt = next(p for p in self.available_prompts if p.name == prompt_name)
                
                # Log prompt details
                logger.debug(f"Prompt object: {prompt}")
                logger.debug(f"Prompt dir: {dir(prompt)}")
                logger.debug(f"Prompt attributes: name={prompt.name}, description={prompt.description}")
                
                # Get parameters
                parameters = {}
                try:
                    if hasattr(prompt, 'arguments') and prompt.arguments:
                        logger.debug(f"Using prompt arguments: {prompt.arguments}")
                        for arg in prompt.arguments:
                            required_marker = " (required)" if getattr(arg, 'required', False) else ""
                            prompt_text = f"> {arg.name}{required_marker}: "
                            param_value = await self.prompt_session.prompt_async(prompt_text)
                            if param_value.strip():
                                # Keep all parameter values as strings
                                parameters[arg.name] = param_value
                    else:
                        logger.warning(f"Prompt {prompt_name} has no arguments attribute")
                        # Fall back to older methods if needed
                        if hasattr(prompt, 'parametersSchema') and prompt.parametersSchema:
                            logger.debug(f"Parameters schema: {prompt.parametersSchema}")
                            for param in json.loads(prompt.parametersSchema).get("properties", {}):
                                param_value = await self.prompt_session.prompt_async(f"> {param}: ")
                                if param_value.strip():
                                    parameters[param] = param_value
                except Exception as e:
                    logger.error(f"Error processing parameters: {e}")
                    console.print(f"[bold red]Error:[/bold red] {str(e)}")
                
                # Execute prompt
                try:
                    with console.status(f"[bold cyan]Executing prompt {prompt_name}...[/bold cyan]"):
                        logger.debug(f"Sending parameters to prompt: {parameters}")
                        prompt_result = await self.session.get_prompt(prompt_name, parameters)
                    
                    logger.debug(f"Prompt result: {prompt_result}")
                    
                    # Display result - handle different response formats
                    if hasattr(prompt_result, 'messages') and isinstance(prompt_result.messages, list):
                        # Handle messages list (MCP 2024 format)
                        content_text = ""
                        prompt_messages = []
                        
                        for message in prompt_result.messages:
                            if hasattr(message, 'content'):
                                if hasattr(message.content, 'text'):
                                    content_text += message.content.text
                                    # Add to messages for Claude
                                    prompt_messages.append({
                                        "role": message.role,
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": message.content.text
                                            }
                                        ]
                                    })
                                elif isinstance(message.content, str):
                                    content_text += message.content
                                    # Add to messages for Claude
                                    prompt_messages.append({
                                        "role": message.role,
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": message.content
                                            }
                                        ]
                                    })
                        
                        # Try to parse the content as JSON if it looks like JSON
                        if content_text.strip().startswith('{') and content_text.strip().endswith('}'):
                            try:
                                json_data = json.loads(content_text)
                                if isinstance(json_data, dict) and 'messages' in json_data:
                                    # Extract the actual message content from nested JSON
                                    prompt_messages = []
                                    for msg in json_data.get('messages', []):
                                        if isinstance(msg, dict) and 'content' in msg and 'text' in msg['content']:
                                            content_text = msg['content']['text']
                                            prompt_messages.append({
                                                "role": msg.get('role', 'user'),
                                                "content": [
                                                    {
                                                        "type": "text",
                                                        "text": msg['content']['text']
                                                    }
                                                ]
                                            })
                            except:
                                # If JSON parsing fails, keep the original content
                                pass
                        
                        # Display the prompt template
                        console.print(Panel(
                            Markdown(content_text),
                            title=f"📝 {prompt_name}",
                            border_style="blue"
                        ))
                        
                        # If we have prompt messages, send them to Claude
                        if prompt_messages:
                            try:
                                # Add the prompt messages to chat history
                                for msg in prompt_messages:
                                    if isinstance(msg, dict):
                                        if 'content' in msg and isinstance(msg['content'], str):
                                            # Format content as a text block for Claude
                                            self.chat_history.append({
                                                "role": msg.get('role', 'user'),
                                                "content": [
                                                    {
                                                        "type": "text",
                                                        "text": msg['content']
                                                    }
                                                ]
                                            })
                                        else:
                                            # Use the message as is
                                            self.chat_history.append(msg)
                                
                                # Get response from Claude
                                with console.status("[bold blue]Getting AI response...[/bold blue]"):
                                    # Get the tools for Claude
                                    anthropic_tools = self.get_anthropic_tools()
                                    
                                    response = self.anthropic.messages.create(
                                        model=MODEL,
                                        max_tokens=4000,
                                        messages=self.chat_history,
                                        tools=anthropic_tools
                                    )
                                
                                # Display Claude's response
                                assistant_message_content = []
                                for content in response.content:
                                    if content.type == "text":
                                        assistant_message_content.append(content)
                                        console.print(Panel(
                                            Markdown(content.text),
                                            title="Claude",
                                            border_style="green"
                                        ))
                                    elif content.type == "tool_use":
                                        # Handle tool use request
                                        tool_name = content.name
                                        tool_args = content.input
                                        tool_id = content.id
                                        
                                        console.print(f"[bold cyan]Claude wants to use tool:[/bold cyan] {tool_name}")
                                        console.print(f"[cyan]Arguments:[/cyan] {json.dumps(tool_args, indent=2)}")
                                        
                                        # Execute the tool
                                        try:
                                            tool_result = await self.execute_tool(tool_name, tool_args)
                                            
                                            # Add tool result to chat history
                                            self.chat_history.append({
                                                "role": "assistant",
                                                "content": [
                                                    {
                                                        "type": "tool_use",
                                                        "id": tool_id,
                                                        "name": tool_name,
                                                        "input": tool_args
                                                    }
                                                ]
                                            })
                                            
                                            # Add tool result to chat history
                                            self.chat_history.append({
                                                "role": "user",
                                                "content": [
                                                    {
                                                        "type": "tool_result",
                                                        "tool_use_id": tool_id,
                                                        "content": tool_result
                                                    }
                                                ]
                                            })
                                            
                                            # Get follow-up response from Claude
                                            with console.status("[bold blue]Processing results...[/bold blue]"):
                                                follow_up_response = self.anthropic.messages.create(
                                                    model=MODEL,
                                                    max_tokens=4000,
                                                    messages=self.chat_history,
                                                    tools=anthropic_tools
                                                )
                                                
                                                # Display follow-up response
                                                for content in follow_up_response.content:
                                                    if content.type == "text":
                                                        console.print(Panel(
                                                            Markdown(content.text),
                                                            title="Claude",
                                                            border_style="green"
                                                        ))
                                        except Exception as e:
                                            console.print(f"[bold red]Error executing tool:[/bold red] {str(e)}")
                                
                                # Add assistant response to chat history
                                self.chat_history.append({
                                    "role": "assistant",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": content.text
                                        } for content in assistant_message_content if hasattr(content, 'text')
                                    ]
                                })
                            except Exception as e:
                                logger.error(f"Error getting AI response: {str(e)}")
                                console.print(f"[bold red]Error getting AI response:[/bold red] {str(e)}")
                    elif hasattr(prompt_result, 'content') and isinstance(prompt_result.content, list):
                        # Handle content list (older format)
                        content_text = ""
                        for content_item in prompt_result.content:
                            if hasattr(content_item, 'text'):
                                content_text += content_item.text
                            elif hasattr(content_item, 'data'):
                                try:
                                    if isinstance(content_item.data, str):
                                        content_text += content_item.data
                                    else:
                                        content_text += json.dumps(content_item.data, indent=2)
                                except:
                                    content_text += str(content_item.data)
                        
                        console.print(Panel(
                            Markdown(content_text),
                            title=f"📝 {prompt_name}",
                            border_style="blue"
                        ))
                    elif hasattr(prompt_result, 'content') and isinstance(prompt_result.content, str):
                        # Handle string content (older format)
                        console.print(Panel(
                            Markdown(prompt_result.content),
                            title=f"📝 {prompt_name}",
                            border_style="blue"
                        ))
                    else:
                        # Fallback for unknown format
                        console.print(Panel(
                            Markdown(str(prompt_result)),
                            title=f"📝 {prompt_name}",
                            border_style="blue"
                        ))
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error executing prompt: {error_msg}")
                    
                    # Handle specific known errors
                    if "PromptParameter" in error_msg:
                        console.print("[bold red]Server Error:[/bold red] The server is using a newer version of the MCP protocol than the client supports.")
                        console.print("This is likely due to a version mismatch between the client and server libraries.")
                        console.print(f"[yellow]Original error:[/yellow] {error_msg}")
                    else:
                        console.print(f"[bold red]Error:[/bold red] {error_msg}")
                return True
            else:
                console.print(f"[yellow]Prompt '{prompt_name}' not found. Available prompts: {', '.join(valid_prompts)}[/yellow]")
                return True
                
        return False
    
    async def handle_help_command(self, query: str) -> bool:
        """Handle help commands.
        
        Args:
            query: The user query
            
        Returns:
            True if command was handled, False otherwise
        """
        if query.strip().lower() in ["help", "?", "commands"]:
            # Generate prompt help text dynamically
            prompt_help = []
            for prompt in self.available_prompts:
                arg_text = ""
                if hasattr(prompt, 'arguments') and prompt.arguments:
                    arg_list = []
                    for arg in prompt.arguments:
                        required = getattr(arg, 'required', False)
                        arg_desc = getattr(arg, 'description', None) or arg.name
                        req_text = " (required)" if required else ""
                        arg_list.append(f"{arg.name}{req_text}: {arg_desc}")
                    if arg_list:
                        arg_text = "\n    Args: " + ", ".join(arg_list)
                
                prompt_help.append(f"- `use prompt {prompt.name}` - {prompt.description}{arg_text}")
            
            help_text = f"""
# Personal Knowledge Assistant - Help

## General Commands:
- `help` - Show this help message
- `clear` - Clear the screen
- `exit` - Exit the application

## Resource Commands:
- `list notes` - List all available notes
- `list documents` - List all available documents

## Prompt Commands:
- `use prompt <name>` - Use a specific prompt template (e.g., 'use prompt summarize')

## Available Prompts:
{chr(10).join(prompt_help)}

## General Usage:
Simply type your questions or requests naturally and Claude will determine when to use tools and resources!

### Example queries:
- "Search the web for information about quantum computing"
- "Create a note about the benefits of exercise"
- "Find notes related to machine learning"
- "Generate a markdown document about climate change"
            """
            console.print(Panel(Markdown(help_text), title="📚 Help", border_style="green"))
            return True
            
        return False
    
    async def run(self) -> None:
        """Run the interactive chat loop."""
        # Connect to server
        await self.connect_to_server()
        
        # Welcome message
        console.print("\n[bold green]Welcome to Personal Knowledge Assistant![/bold green]")
        console.print("Type [bold]help[/bold] for available commands or [bold]exit[/bold] to quit.")
        console.print("[bold yellow]To use a prompt:[/bold yellow] Type [bold]use prompt <name>[/bold] (e.g., 'use prompt summarize')\n")
        
        # Main loop
        while True:
            try:
                # Get user input
                query = await self.prompt_session.prompt_async("You: ")
                
                # Handle exit command
                if query.strip().lower() in ["exit", "quit", "bye"]:
                    console.print("[green]Goodbye![/green]")
                    break
                
                # Handle clear command
                if query.strip().lower() == "clear":
                    console.clear()
                    continue
                
                # Handle help command
                if await self.handle_help_command(query):
                    continue
                
                # Handle resource commands
                if await self.handle_resource_commands(query):
                    continue
                
                # Process normal query
                await self.process_query(query)
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Interrupted by user[/bold yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    async def close(self) -> None:
        """Close connections and clean up."""
        if self.session:
            await self.exit_stack.aclose()


async def main():
    """Main entry point for the application."""
    # Parse command line arguments
    server_path = DEFAULT_SERVER_PATH
    if len(sys.argv) > 1:
        server_path = sys.argv[1]
    
    # Create and run client
    client = PersonalKnowledgeAssistantClient(server_path)
    try:
        await client.run()
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exiting...[/bold yellow]")
