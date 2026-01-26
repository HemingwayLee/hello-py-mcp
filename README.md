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
