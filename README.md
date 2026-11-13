# Hello MCP Server

A simple MCP (Model Context Protocol) server that provides a greeting tool,
built with the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) v2 (`MCPServer`).
* It is not necessary to listen on a port. The default transport is `stdio`.
  * It talks to the client over standard input and output, so whatever (e.g., Ollama, Claude Code) launches it as a subprocess (like our MCP [client](https://github.com/HemingwayLee/hello-py-mcp/tree/main/client)) communicates with it directly

## Terminology

In MCP, "server" names the program's **role**, not whether it uses the network. This
project is a **stdio MCP server** (also called a local MCP server). The MCP spec defines
three roles:

| Role | What it is | In this project |
|---|---|---|
| **Host** | The app the user works in, which runs the model | Claude Desktop, Claude Code, or Continue.dev / Open WebUI with Ollama |
| **Client** | The connection the host opens to one server | Built into each host, or [`client/test_client.py`](client/test_client.py) |
| **Server** | The program that provides tools, resources and prompts | [`server.py`](server.py) |

The transport (`stdio` or `streamable-http`) only decides how messages travel. With
`stdio`, the client starts the server as a subprocess, so no port is needed.

## Prerequisites

- Python 3.10 or higher (`mcp` won't install on older versions; on macOS the
  system `python3` may be 3.9, so use a newer one, e.g. from Homebrew or `uv`)

## Installation

1. Create and activate a virtual environment:

```bash
python3 -m venv venv   # make sure this python3 is 3.10+
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

The server communicates over stdio and is designed to be launched by an MCP client,
so running it by hand just waits for input (press Ctrl+C to exit). To try it out
interactively, use the MCP Inspector (see [Testing with MCP Inspector](#testing-with-mcp-inspector)).

> **Note:** MCP clients usually launch the server with an absolute command path and
> without activating your virtualenv. In the client configs below, point `command` at
> the virtualenv's interpreter (e.g. `/absolute/path/to/hello-py-mcp/venv/bin/python`,
> or `venv\Scripts\python.exe` on Windows), not a bare `python`. Otherwise the
> client may pick a Python that doesn't have `mcp` installed.

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
      "command": "/absolute/path/to/hello-py-mcp/venv/bin/python",
      "args": ["/absolute/path/to/hello-py-mcp/server.py"]
    }
  }
}
```

Replace `/absolute/path/to/hello-py-mcp` with the actual path to this project, then restart Claude Desktop.

## Using with Claude Code

Register the server with Claude Code:

```bash
claude mcp add hello -- /absolute/path/to/hello-py-mcp/venv/bin/python /absolute/path/to/hello-py-mcp/server.py
```

Then run `claude mcp list` to check that it's connected, or type `/mcp` inside a Claude Code session.

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
      "command": "/absolute/path/to/hello-py-mcp/venv/bin/python",
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

## Automated Test Client

[`client/test_client.py`](client/test_client.py) starts the server over stdio and runs
end-to-end protocol checks (handshake, ping, tools/list, valid and invalid tool calls).
It exits with a non-zero status if any check fails:

```bash
python client/test_client.py
```

See [`client/README.md`](client/README.md) for details.

## Testing with MCP Inspector

You can test the MCP server directly using the MCP Inspector (requires Node.js).
Run this from the project directory with the virtualenv activated:

```bash
npx @modelcontextprotocol/inspector python server.py
```

This opens a web interface where you can test your MCP server's tools manually, regardless of which LLM you plan to use.
