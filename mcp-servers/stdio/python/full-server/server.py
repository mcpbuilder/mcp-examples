#!/usr/bin/env python3
"""
Personal Knowledge Assistant - MCP Server

This server demonstrates a full implementation of the Model Context Protocol (MCP)
with tools, resources, and prompts. It helps users research topics, manage notes,
and generate content.
"""

import os
import json
import time
import re
import uuid
import asyncio
import requests
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import markdown
from fastmcp import FastMCP
import mcp.types as types

# Set up logging to file
log_file = "/tmp/mcp_server.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server")

# Initialize data directories
DATA_DIR = Path("./data")
NOTES_DIR = DATA_DIR / "notes"
DOCUMENTS_DIR = DATA_DIR / "documents"
RESOURCES_DIR = DATA_DIR / "resources"

# Create directories if they don't exist
for directory in [NOTES_DIR, DOCUMENTS_DIR, RESOURCES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Initialize the server
server = FastMCP(name="personal-knowledge-assistant")

#-------------------------------------------------------
# Tools Section - Research, Notes, and Content Generation
#-------------------------------------------------------

@server.tool()
async def search_web(query: str, max_results: int = 5) -> dict:
    """
    Search the web for information on a topic.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary containing search results
    """
    # Simulate web search
    try:
        # In a real implementation, this would use a proper search API
        time.sleep(1)  # Simulate network delay
        
        results = []
        for i in range(max_results):
            results.append({
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"This is a snippet of the search result {i+1} for your query about {query}...",
            })
            
        return {
            "success": True,
            "results": results,
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@server.tool()
async def fetch_webpage_content(url: str) -> dict:
    """
    Fetch and extract the main content from a webpage.
    
    Args:
        url: The URL of the webpage to fetch
        
    Returns:
        Dictionary containing the webpage content
    """
    try:
        # Simulated response for demo purposes
        if "example.com" in url:
            return {
                "success": True,
                "title": f"Example Page for {url}",
                "content": f"This is simulated content for {url}. In a real implementation, this would fetch and extract the main content from the actual webpage.",
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        
        # For real URLs, attempt to fetch content
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract main content (simplified)
        main_content = ""
        for paragraph in soup.find_all('p'):
            main_content += paragraph.get_text() + "\n\n"
        
        return {
            "success": True,
            "title": title,
            "content": main_content[:10000],  # Limit content size
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }

@server.tool()
async def create_note(title: str, content: str, tags: list = None) -> dict:
    """
    Create a new note in the knowledge base.
    
    Args:
        title: Title of the note
        content: The note content
        tags: List of tags for the note
        
    Returns:
        Dictionary with note information
    """
    try:
        if tags is None:
            tags = []
            
        # Create a note ID from title
        note_id = str(uuid.uuid4())
        safe_title = re.sub(r'[^\w\-]', '_', title.lower())
        
        note_data = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save the note
        note_path = NOTES_DIR / f"{safe_title}_{note_id[:8]}.json"
        with open(note_path, 'w') as f:
            json.dump(note_data, f, indent=2)
            
        return {
            "success": True,
            "note_id": note_id,
            "title": title,
            "path": str(note_path),
            "message": f"Note '{title}' created successfully!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@server.tool()
async def find_notes(query: str = None, tags: list = None) -> dict:
    """
    Search for notes in the knowledge base.
    
    Args:
        query: Search term for note content/title
        tags: List of tags to filter notes
        
    Returns:
        Dictionary with matching notes
    """
    try:
        results = []
        
        # Load all notes
        for note_file in NOTES_DIR.glob("*.json"):
            try:
                with open(note_file, 'r') as f:
                    note = json.load(f)
                
                # Filter by query
                if query and query.lower() not in note["title"].lower() and query.lower() not in note["content"].lower():
                    continue
                    
                # Filter by tags
                if tags and not all(tag in note["tags"] for tag in tags):
                    continue
                    
                # Add to results
                results.append({
                    "id": note["id"],
                    "title": note["title"],
                    "tags": note["tags"],
                    "created_at": note["created_at"],
                    "updated_at": note["updated_at"],
                    "preview": note["content"][:150] + "..." if len(note["content"]) > 150 else note["content"]
                })
            except Exception as e:
                continue
                
        return {
            "success": True,
            "query": query,
            "tags": tags,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@server.tool()
async def generate_markdown_doc(title: str, sections: list, content_type: str = "article") -> dict:
    """
    Generate a structured Markdown document.
    
    Args:
        title: Title of the document
        sections: List of section titles
        content_type: Type of content (article, notes, tutorial)
        
    Returns:
        Dictionary with the generated document
    """
    try:
        doc_id = str(uuid.uuid4())
        safe_title = re.sub(r'[^\w\-]', '_', title.lower())
        
        markdown_content = f"# {title}\n\n"
        markdown_content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        # Add sections
        for i, section in enumerate(sections):
            markdown_content += f"## {section}\n\n"
            markdown_content += f"Content for section {i+1}: {section}. Replace this with actual content.\n\n"
        
        # Add a footer
        markdown_content += "---\n"
        markdown_content += f"*This document was generated by the Personal Knowledge Assistant.*"
        
        # Save the document
        doc_path = DOCUMENTS_DIR / f"{safe_title}_{doc_id[:8]}.md"
        with open(doc_path, 'w') as f:
            f.write(markdown_content)
            
        # Also save as HTML for preview
        html_content = markdown.markdown(markdown_content)
        html_path = DOCUMENTS_DIR / f"{safe_title}_{doc_id[:8]}.html"
        with open(html_path, 'w') as f:
            f.write(f"<!DOCTYPE html><html><head><title>{title}</title></head><body>{html_content}</body></html>")
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": title,
            "content": markdown_content,
            "markdown_path": str(doc_path),
            "html_path": str(html_path),
            "message": f"Document '{title}' generated successfully!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

#-------------------------------------------------------
# Resources Section - Knowledge Base Access
#-------------------------------------------------------

@server.resource("notes:{uri}")
async def get_notes_resource(uri: str) -> types.ResourceReference:
    """Resource handler for accessing notes."""
    try:
        # Handle listing all notes
        if uri == "notes:list":
            notes_list = []
            for note_file in NOTES_DIR.glob("*.json"):
                try:
                    with open(note_file, 'r') as f:
                        note = json.load(f)
                    notes_list.append({
                        "id": note["id"],
                        "title": note["title"],
                        "tags": note["tags"],
                        "updated_at": note["updated_at"]
                    })
                except Exception:
                    continue
            
            return types.ResourceReadResponse(
                uri=uri,
                title="All Notes",
                content=[
                    types.Content(
                        type="application/json",
                        data=json.dumps(notes_list, indent=2)
                    )
                ]
            )
        
        # Handle retrieving specific note by ID
        if uri.startswith("notes:id:"):
            note_id = uri.split("notes:id:")[1]
            for note_file in NOTES_DIR.glob("*.json"):
                try:
                    with open(note_file, 'r') as f:
                        note = json.load(f)
                    if note["id"] == note_id or note_file.stem.endswith(note_id[:8]):
                        return types.ResourceReadResponse(
                            uri=uri,
                            title=note["title"],
                            content=[
                                types.Content(
                                    type="text/markdown",
                                    data=f"# {note['title']}\n\n{note['content']}\n\nTags: {', '.join(note['tags'])}"
                                )
                            ]
                        )
                except Exception:
                    continue
            
            return types.ResourceReadResponse(
                uri=uri,
                title="Note Not Found",
                content=[
                    types.Content(
                        type="text/plain",
                        data=f"Note with ID {note_id} not found."
                    )
                ],
                is_error=True
            )
        
        # Handle search
        if uri.startswith("notes:search:"):
            search_query = uri.split("notes:search:")[1]
            matching_notes = []
            
            for note_file in NOTES_DIR.glob("*.json"):
                try:
                    with open(note_file, 'r') as f:
                        note = json.load(f)
                    if search_query.lower() in note["title"].lower() or search_query.lower() in note["content"].lower():
                        matching_notes.append({
                            "id": note["id"],
                            "title": note["title"],
                            "preview": note["content"][:150] + "..." if len(note["content"]) > 150 else note["content"],
                            "tags": note["tags"]
                        })
                except Exception:
                    continue
            
            return types.ResourceReadResponse(
                uri=uri,
                title=f"Search Results for '{search_query}'",
                content=[
                    types.Content(
                        type="application/json",
                        data=json.dumps(matching_notes, indent=2)
                    )
                ]
            )
        
        # Default response for unknown URI
        return types.ResourceReadResponse(
            uri=uri,
            title="Unknown Resource",
            content=[
                types.Content(
                    type="text/plain",
                    data="Unknown resource URI pattern. Valid patterns are: notes:list, notes:id:<id>, notes:search:<query>"
                )
            ],
            is_error=True
        )
    except Exception as e:
        return types.ResourceReadResponse(
            uri=uri,
            title="Error",
            content=[
                types.Content(
                    type="text/plain",
                    data=f"Error: {str(e)}"
                )
            ],
            is_error=True
        )

@server.resource("documents:{uri}")
async def get_documents_resource(uri: str) -> types.ResourceReference:
    """Resource handler for accessing documents."""
    try:
        # Handle listing all documents
        if uri == "documents:list":
            docs_list = []
            for doc_file in DOCUMENTS_DIR.glob("*.md"):
                try:
                    # Get first line as title
                    with open(doc_file, 'r') as f:
                        first_line = f.readline().strip()
                        title = first_line.lstrip("# ")
                    
                    docs_list.append({
                        "id": doc_file.stem.split("_")[-1],
                        "title": title,
                        "path": str(doc_file),
                        "updated_at": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
                    })
                except Exception:
                    continue
            
            return types.ResourceReadResponse(
                uri=uri,
                title="All Documents",
                content=[
                    types.Content(
                        type="application/json",
                        data=json.dumps(docs_list, indent=2)
                    )
                ]
            )
        
        # Handle retrieving specific document by ID
        if uri.startswith("documents:id:"):
            doc_id = uri.split("documents:id:")[1]
            for doc_file in DOCUMENTS_DIR.glob("*.md"):
                if doc_id in doc_file.stem:
                    try:
                        with open(doc_file, 'r') as f:
                            content = f.read()
                        
                        return types.ResourceReadResponse(
                            uri=uri,
                            title=doc_file.stem,
                            content=[
                                types.Content(
                                    type="text/markdown",
                                    data=content
                                )
                            ]
                        )
                    except Exception as e:
                        return types.ResourceReadResponse(
                            uri=uri,
                            title="Error Reading Document",
                            content=[
                                types.Content(
                                    type="text/plain",
                                    data=f"Error reading document: {str(e)}"
                                )
                            ],
                            is_error=True
                        )
            
            return types.ResourceReadResponse(
                uri=uri,
                title="Document Not Found",
                content=[
                    types.Content(
                        type="text/plain",
                        data=f"Document with ID {doc_id} not found."
                    )
                ],
                is_error=True
            )
        
        # Default response for unknown URI
        return types.ResourceReadResponse(
            uri=uri,
            title="Unknown Resource",
            content=[
                types.Content(
                    type="text/plain",
                    data="Unknown resource URI pattern. Valid patterns are: documents:list, documents:id:<id>"
                )
            ],
            is_error=True
        )
    except Exception as e:
        return types.ResourceReadResponse(
            uri=uri,
            title="Error",
            content=[
                types.Content(
                    type="text/plain",
                    data=f"Error: {str(e)}"
                )
            ],
            is_error=True
        )

#-------------------------------------------------------
# Prompts Section - Reusable Templates
#-------------------------------------------------------

@server.prompt("summarize")
async def summarize_prompt(context: str, target_length: str = "medium") -> types.GetPromptResult:
    """
    Prompt for summarizing content at different lengths.
    
    Args:
        context: The content to summarize
        target_length: The target length of the summary (short, medium, long)
    """
    length_guide = {
        "short": "1-2 sentences",
        "medium": "a paragraph",
        "long": "multiple paragraphs with headings"
    }
    
    target = length_guide.get(target_length, length_guide["medium"])
    
    template = f"""## Summarization Task

You are tasked with creating a clear and informative summary of the following content:

```content
{context}
```

### Instructions:
- Create a summary that is approximately {target} in length
- Capture the most important information and key points
- Maintain the original meaning and intent
- Use clear, concise language
- Do not include your own opinions or additional information

Please provide only the summary in your response, without explanations or meta-commentary.
"""
    
    return types.GetPromptResult(
        description=f"Summarize content to {target_length} length",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=template
                )
            )
        ]
    )

@server.prompt("ideastorm")
async def ideastorm_prompt(
    topic: str, perspective: str = "general", count: int = 10
) -> types.GetPromptResult:
    """
    Prompt for generating creative ideas on a topic.
    
    Args:
        topic: The subject to generate ideas about
        perspective: The perspective to consider
        count: Number of ideas to generate
    """
    # Ensure count is within reasonable limits
    count = max(1, min(20, count))
    
    template = f"""
# Creative Idea Storm: {topic}

## Task
Generate {count} innovative and thought-provoking ideas related to {topic}.

## Perspective
Consider the {perspective} perspective when generating these ideas.

## Format
Present each idea as a numbered list item with a brief title and 1-2 sentence explanation.

1. [Idea Title]: Brief explanation of the idea.
2. [Idea Title]: Brief explanation of the idea.
...etc.
"""

    # Create a message for the prompt
    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=template
            )
        )
    ]

    return types.GetPromptResult(
        description=f"Generate innovative ideas related to {topic}",
        messages=messages
    )

@server.prompt("structured_analysis")
async def structured_analysis_prompt(
    text: str, 
    analysis_type: str = "general", 
    include_summary: bool = True
) -> types.GetPromptResult:
    """
    Prompt for conducting structured analysis of text.
    
    Args:
        text: The text to analyze
        analysis_type: Type of analysis (general, academic, business)
        include_summary: Whether to include a summary
    """
    analysis_instructions = {
        "general": "Analyze the main themes, arguments, and notable elements of the text.",
        "academic": "Conduct a scholarly analysis focusing on methodology, theoretical frameworks, and evidence quality.",
        "business": "Analyze business implications, market insights, and strategic recommendations."
    }
    
    instruction = analysis_instructions.get(analysis_type, analysis_instructions["general"])
    summary_section = "- Begin with a brief summary of the text\n" if include_summary else ""
    
    template = f"""## Structured Analysis

Perform a {analysis_type} analysis of the following text:

```
{text}
```

### Analysis Instructions:
{instruction}

### Your response should include:
{summary_section}- Key insights and findings
- Critical evaluation of main points
- Identification of strengths and weaknesses
- Contextual significance
- Organize your analysis with clear headings and structure

Provide a thorough, objective analysis that offers meaningful insights.
"""
    
    return types.GetPromptResult(
        description=f"Perform a structured {analysis_type} analysis of text",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=template
                )
            )
        ]
    )

#-------------------------------------------------------
# Resource Roots Handler
#-------------------------------------------------------

@server.tool()
async def get_resource_roots() -> dict:
    """
    Get the resource roots available in the server.
    
    Returns:
        Dictionary containing the resource roots
    """
    logger.debug("get_resource_roots tool called")
    result = {
        "success": True,
        "roots": ["notes", "documents", "resources"]
    }
    logger.debug(f"Returning resource roots: {result}")
    return result

#-------------------------------------------------------
# Main Execution
#-------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting Personal Knowledge Assistant MCP Server...")
    server.run(transport="stdio")
