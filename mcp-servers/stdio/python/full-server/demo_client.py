#!/usr/bin/env python3
"""
Demo Client for Personal Knowledge Assistant MCP Server

This script provides a narrative-based demonstration of how a client
might interact with the Personal Knowledge Assistant MCP server.
It tells a story through a series of interactions with the server's
tools, resources, and prompts.
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

# Configuration
SERVER_PATH = Path(__file__).parent / "server.py"

class MCPClient:
    """Simple MCP client for demonstration purposes"""
    
    def __init__(self, server_path):
        self.server_path = server_path
        self.server_process = None
        self.server_started = False
        
    def start_server(self):
        """Start the MCP server process"""
        print("Starting MCP server...")
        # Make sure server script is executable
        os.chmod(self.server_path, 0o755)
        
        # Start server as subprocess
        self.server_process = subprocess.Popen(
            [self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Give the server time to start
        time.sleep(2)
        self.server_started = True
        print("MCP server started!")
        
    def stop_server(self):
        """Stop the MCP server process"""
        if self.server_process:
            print("Stopping MCP server...")
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            self.server_started = False
            print("MCP server stopped!")
            
    def send_request(self, method, params=None):
        """Send request to MCP server"""
        if not self.server_started:
            raise RuntimeError("Server not started")
            
        request_id = int(time.time() * 1000)
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        # Send request to server
        request_str = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_str)
        self.server_process.stdin.flush()
        
        # Read response from server
        response_str = self.server_process.stdout.readline().strip()
        response = json.loads(response_str)
        
        if "error" in response:
            print(f"Error: {response['error']}")
        
        return response
        
    def __enter__(self):
        self.start_server()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_server()

async def run_demo():
    """Run the narrative demo"""
    with MCPClient(SERVER_PATH) as client:
        print("\n" + "="*80)
        print("Personal Knowledge Assistant Demo".center(80))
        print("="*80 + "\n")
        
        print("This demo will showcase a narrative of how a user might interact with")
        print("the Personal Knowledge Assistant MCP server through an AI assistant.\n")

        # Act 1: Introduction and Discovery
        print("\n📘 ACT 1: INTRODUCTION & DISCOVERY")
        print("-----------------------------------")
        
        print("\n[User]: I'd like to research renewable energy technologies.")
        print("[AI Assistant]: I'll help you research renewable energy technologies.")
        print("          Let me check what capabilities I have access to...\n")
        
        # Discover tools
        print("🔍 Discovering tools...")
        tools_response = client.send_request("tool/list")
        tools = tools_response.get("result", {}).get("tools", [])
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
            
        # Discover resources
        print("\n🔍 Discovering resources...")
        resources_response = client.send_request("resources/list")
        resources = resources_response.get("result", {}).get("uriPatterns", [])
        print(f"Found resource patterns:")
        for resource in resources:
            print(f"  - {resource}")
            
        # Discover prompts
        print("\n🔍 Discovering prompts...")
        prompts_response = client.send_request("prompts/list")
        prompts = prompts_response.get("result", {}).get("prompts", [])
        print(f"Found {len(prompts)} prompts:")
        for prompt in prompts:
            print(f"  - {prompt['id']}: {prompt['description']}")
            
        # Act 2: Research and Note Taking
        print("\n\n📙 ACT 2: RESEARCH & NOTE TAKING")
        print("--------------------------------")
        
        print("\n[User]: Great, please search for information about solar and wind energy.")
        print("[AI Assistant]: I'll search for information about solar and wind energy.\n")
        
        # Search for information
        print("🔍 Searching the web...")
        search_response = client.send_request("tool/execute", {
            "name": "search_web",
            "params": {
                "query": "solar and wind energy technologies",
                "max_results": 3
            }
        })
        search_results = search_response.get("result", {}).get("result", {}).get("results", [])
        print(f"Found {len(search_results)} results:")
        for i, result in enumerate(search_results):
            print(f"  {i+1}. {result['title']}")
            print(f"     URL: {result['url']}")
            print(f"     {result['snippet']}")
            
        # Fetch content from a result
        print("\n[User]: Can you get more details from the first result?")
        print("[AI Assistant]: I'll fetch the content from the first search result.\n")
        
        print("📄 Fetching webpage content...")
        first_url = search_results[0]["url"]
        content_response = client.send_request("tool/execute", {
            "name": "fetch_webpage_content",
            "params": {
                "url": first_url
            }
        })
        page_content = content_response.get("result", {}).get("result", {})
        print(f"Title: {page_content.get('title', 'No title')}")
        print(f"Content preview: {page_content.get('content', 'No content')[:200]}...\n")
        
        # Create a note
        print("\n[User]: Please save this information as a note.")
        print("[AI Assistant]: I'll create a note with this information.\n")
        
        print("📝 Creating a note...")
        note_response = client.send_request("tool/execute", {
            "name": "create_note",
            "params": {
                "title": "Renewable Energy Technologies",
                "content": f"# Renewable Energy Technologies\n\nSource: {first_url}\n\n{page_content.get('content', 'No content')[:500]}...",
                "tags": ["energy", "renewable", "research"]
            }
        })
        note_result = note_response.get("result", {}).get("result", {})
        print(f"Note created: {note_result.get('title')}")
        print(f"Note ID: {note_result.get('note_id')}")
        print(f"Saved to: {note_result.get('path')}\n")
        
        # Act 3: Using Prompts for Content Generation
        print("\n\n📕 ACT 3: USING PROMPTS FOR CONTENT GENERATION")
        print("--------------------------------------------")
        
        print("\n[User]: Can you generate some creative ideas for implementing renewable energy?")
        print("[AI Assistant]: I'll use a prompt template to generate creative ideas.\n")
        
        # Get the idea generation prompt
        print("📋 Retrieving idea generation prompt...")
        prompt_response = client.send_request("prompts/get", {
            "id": "ideastorm",
            "params": {
                "topic": "implementing renewable energy in urban environments",
                "perspective": "urban planning",
                "count": 5
            }
        })
        prompt_template = prompt_response.get("result", {}).get("template", "")
        print(f"Prompt template retrieved:")
        print(f"\n{prompt_template}\n")
        
        print("\n[AI Assistant]: Here's a creative ideation prompt I can use with an LLM...")
        print("[User]: Perfect! And after that, can you create a document outline?")
        print("[AI Assistant]: I'll generate a structured document with key sections.\n")
        
        # Generate a markdown document
        print("📄 Generating a markdown document...")
        doc_response = client.send_request("tool/execute", {
            "name": "generate_markdown_doc",
            "params": {
                "title": "Urban Renewable Energy Implementation Guide",
                "sections": [
                    "Introduction to Urban Renewable Energy",
                    "Solar Technologies for Urban Environments",
                    "Wind Energy Solutions for Cities",
                    "Energy Storage Considerations",
                    "Policy Recommendations",
                    "Case Studies",
                    "Implementation Roadmap"
                ],
                "content_type": "guide"
            }
        })
        doc_result = doc_response.get("result", {}).get("result", {})
        print(f"Document generated: {doc_result.get('title')}")
        print(f"Saved to: {doc_result.get('markdown_path')}")
        print(f"\nDocument content preview:\n")
        print(doc_result.get('content', '')[:500] + "...\n")
        
        # Act 4: Resource Access and Analysis
        print("\n\n📗 ACT 4: RESOURCE ACCESS & ANALYSIS")
        print("-----------------------------------")
        
        print("\n[User]: Can you show me all the notes I have?")
        print("[AI Assistant]: I'll retrieve your notes using resource access.\n")
        
        # Access notes resource
        print("📚 Accessing notes resource...")
        notes_resource = client.send_request("resources/read", {
            "uri": "notes:list"
        })
        notes_content = notes_resource.get("result", {}).get("content", [])
        if notes_content:
            notes_data = json.loads(notes_content[0].get("data", "[]"))
            print(f"Found {len(notes_data)} notes:")
            for note in notes_data:
                print(f"  - {note.get('title')} (Tags: {', '.join(note.get('tags', []))})")
        
        # Access documents resource
        print("\n[User]: What documents do I have available?")
        print("[AI Assistant]: Let me check your documents.\n")
        
        print("📚 Accessing documents resource...")
        docs_resource = client.send_request("resources/read", {
            "uri": "documents:list"
        })
        docs_content = docs_resource.get("result", {}).get("content", [])
        if docs_content:
            docs_data = json.loads(docs_content[0].get("data", "[]"))
            print(f"Found {len(docs_data)} documents:")
            for doc in docs_data:
                print(f"  - {doc.get('title')} (Updated: {doc.get('updated_at')})")
        
        # Use analysis prompt
        print("\n[User]: Can you analyze the renewable energy document from a business perspective?")
        print("[AI Assistant]: I'll use a structured analysis prompt for this task.\n")
        
        print("📋 Retrieving analysis prompt...")
        analysis_response = client.send_request("prompts/get", {
            "id": "structured_analysis",
            "params": {
                "text": doc_result.get('content', '')[:1000],
                "analysis_type": "business",
                "include_summary": True
            }
        })
        analysis_template = analysis_response.get("result", {}).get("template", "")
        print(f"Analysis prompt template retrieved:")
        print(f"\n{analysis_template[:500]}...\n")
        
        # Conclusion
        print("\n\n📚 CONCLUSION")
        print("-----------")
        
        print("\nThis demo has showcased the key capabilities of the Personal Knowledge Assistant:")
        print("  1. Tools for research, note-taking, and content generation")
        print("  2. Resources for accessing stored knowledge")
        print("  3. Prompts for structured content creation and analysis")
        print("\nA real MCP client would connect these capabilities to an LLM like Claude")
        print("to provide an intelligent assistant that can help with knowledge work.")
        print("\nEnd of demonstration.\n")

if __name__ == "__main__":
    asyncio.run(run_demo())
