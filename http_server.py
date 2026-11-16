from typing import Annotated

import uvicorn
from mcp.server.mcpserver import MCPServer
from pydantic import Field
from starlette.middleware.cors import CORSMiddleware

HOST = "0.0.0.0"
PORT = 1234

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
    app = mcp.streamable_http_app(host=HOST)

    # Allow browser pages from any origin (including an HTML file opened from disk,
    # whose origin is "null") to call the server, e.g. http_client/index.html.
    # Browsers hide response headers from JavaScript unless they are exposed, and the
    # client must read Mcp-Session-Id to continue the session after the handshake.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )

    uvicorn.run(app, host=HOST, port=PORT)
