from typing import Annotated

from mcp.server.mcpserver import MCPServer
from pydantic import Field

mcp = MCPServer("hello-server")


@mcp.tool()
def hello(
    name: Annotated[str, Field(description="The name of the person to greet")],
) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    # Streamable HTTP transport: serves the MCP endpoint at http://<this-machine>:1234/mcp
    # Listens on all network interfaces, so other machines can reach it (no authentication).
    mcp.run(transport="streamable-http", host="0.0.0.0", port=1234)
