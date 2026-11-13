"""Smoke-test client for the hello MCP server.

Launches ../server.py over stdio (using the same Python interpreter that runs
this script), then exercises the protocol end to end:

  1. initialize handshake
  2. ping
  3. tools/list
  4. tools/call with valid arguments
  5. tools/call with a missing required argument (expects an error result)
  6. tools/call for an unknown tool (expects an error result)

Exits with status 0 if every check passes, 1 otherwise.

Usage:
    python client/test_client.py [path/to/server.py]
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DEFAULT_SERVER = Path(__file__).resolve().parent.parent / "server.py"

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" -> {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def text_of(result) -> str:
    return " ".join(getattr(c, "text", "") for c in result.content)


async def run(server_path: Path) -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(server_path)])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Handshake
            init = await session.initialize()
            check(
                "initialize",
                init.server_info.name == "hello-server",
                f"server={init.server_info.name!r}",
            )
            check("server declares tools capability", init.capabilities.tools is not None)

            # 2. Ping
            await session.send_ping()
            check("ping", True)

            # 3. List tools
            tools = {t.name: t for t in (await session.list_tools()).tools}
            check("tools/list includes 'hello'", "hello" in tools, f"tools={sorted(tools)}")
            if "hello" in tools:
                schema = tools["hello"].input_schema
                check(
                    "'hello' schema requires 'name'",
                    "name" in schema.get("required", []),
                    f"schema={schema}",
                )

            # 4. Valid call
            result = await session.call_tool("hello", {"name": "Alice"})
            check(
                "call hello(name='Alice')",
                not result.is_error and text_of(result) == "Hello, Alice!",
                repr(text_of(result)),
            )

            # 5. Missing required argument -> error result, not a crash
            result = await session.call_tool("hello", {})
            check("call hello() without name returns error", result.is_error)

            # 6. Unknown tool -> error result, not a crash
            result = await session.call_tool("does_not_exist", {})
            check("call unknown tool returns error", result.is_error)


def main() -> int:
    server_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_SERVER
    if not server_path.is_file():
        print(f"Server script not found: {server_path}", file=sys.stderr)
        return 1

    print(f"Testing MCP server: {server_path}\n")
    try:
        asyncio.run(run(server_path))
    except Exception as exc:  # connection failures, server crashes, etc.
        # anyio wraps errors in (nested) exception groups; report the root cause.
        # (duck-typed so this also works on Python 3.10, which has no built-in
        # BaseExceptionGroup)
        while len(getattr(exc, "exceptions", ())) == 1:
            exc = exc.exceptions[0]
        print(f"[FAIL] session aborted: {type(exc).__name__}: {exc}")
        print("       (check the server's stderr output above for its traceback)")
        failures.append("session")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
