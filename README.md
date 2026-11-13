# Hello MCP Server

A simple MCP (Model Context Protocol) server that provides a greeting tool.

## Prerequisites

- Python 3.10 or higher

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or using pyproject.toml:

```bash
pip install -e .
```

## Running the Server

Run the server directly:

```bash
python server.py
```

The server communicates over stdio and is designed to be launched by an MCP client.

## Available Tools

### `hello`

Says hello to someone.

**Parameters:**
- `name` (string, required): The name of the person to greet

**Example response:** `Hello, Alice!`

## Using with Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hello": {
      "command": "python",
      "args": ["/absolute/path/to/hello-py-mcp/server.py"]
    }
  }
}
```

Replace `/absolute/path/to/hello-py-mcp` with the actual path to this project.

## Using with Claude Code

Run Claude Code with the MCP server:

```bash
claude --mcp-server "python /absolute/path/to/hello-py-mcp/server.py"
```

## Using with Ollama

Ollama doesn't natively support MCP servers, but you can use them together through various methods:

### Option 1: Using Continue.dev (VS Code/JetBrains)

[Continue.dev](https://continue.dev) is an IDE extension that supports both Ollama and MCP servers.

1. Install the Continue extension in VS Code or JetBrains
2. Configure your `~/.continue/config.json`:

```json
{
  "models": [{
    "title": "Ollama",
    "provider": "ollama",
    "model": "llama3.2"
  }],
  "mcpServers": {
    "hello": {
      "command": "python",
      "args": ["/absolute/path/to/hello-py-mcp/server.py"]
    }
  }
}
```

Replace `/absolute/path/to/hello-py-mcp` with the actual path to this project and adjust the Ollama model name as needed.

### Option 2: Using Open WebUI

[Open WebUI](https://github.com/open-webui/open-webui) supports MCP servers and works with Ollama.

1. Install and run Open WebUI (connects to Ollama by default)
2. Configure MCP server in Settings → Tools → MCP Servers

### Option 3: Custom Integration

You can build a custom client using the MCP Python SDK and Ollama's API:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama

async def main():
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

            # Use Ollama to generate a response
            response = ollama.chat(
                model='llama3.2',
                messages=[{
                    'role': 'user',
                    'content': 'Say hello to Alice'
                }]
            )

            # Call MCP tool based on LLM response
            result = await session.call_tool("hello", {"name": "Alice"})
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Option 4: Using MCP Client CLI

You can test the MCP server directly using the MCP inspector:

```bash
npx @modelcontextprotocol/inspector python server.py
```

This opens a web interface where you can test your MCP server's tools manually, regardless of which LLM you plan to use.
