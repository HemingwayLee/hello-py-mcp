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
    mcp.run()  # stdio transport by default
