# MCP Client Examples

This directory contains examples of Model Context Protocol (MCP) clients implemented in different programming languages.

MCP clients connect to MCP servers and allow applications to leverage the tools, resources, and prompts exposed by those servers. These examples demonstrate how to build clients that can connect to and interact with MCP servers.

## Available Examples

- [Basic Python Client](./python-basic-client/): A simple Python-based MCP client that demonstrates how to connect to an MCP server and use its tools.
- [UV Python Client](./uv-python-basic-client/): A Python MCP client that uses the `uv` package manager for simplified dependency management and single-file execution.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. It follows a client-server architecture where a host application can connect to multiple servers.

MCP helps you build agents and complex workflows on top of LLMs by providing:
- A growing list of pre-built integrations that your LLM can directly plug into
- The flexibility to switch between LLM providers and vendors
- Best practices for securing your data within your infrastructure

For more information, visit the [Model Context Protocol website](https://modelcontextprotocol.io/).
