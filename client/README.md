# MCP Test Client

A small MCP client that tests the hello server ([`../server.py`](../server.py)) end to end.
It starts the server as a subprocess over stdio, the same way Claude Desktop and Claude Code
do, and runs a series of protocol checks.

## What it checks

| # | Check | Expected |
|---|-------|----------|
| 1 | `initialize` handshake | Server reports name `hello-server` and declares the `tools` capability |
| 2 | `ping` | Server responds |
| 3 | `tools/list` | Includes `hello`, whose input schema requires `name` |
| 4 | `tools/call hello {"name": "Alice"}` | Returns `Hello, Alice!` |
| 5 | `tools/call hello {}` (missing `name`) | Returns an error result (`is_error: true`), not a crash |
| 6 | `tools/call does_not_exist {}` | Returns an error result (`is_error: true`), not a crash |

## Prerequisites

The client uses the same dependencies as the server (Python 3.10+ and `mcp>=2`).
Set them up from the repository root as described in the [main README](../README.md#installation):

```bash
python3 -m venv venv          # make sure this python3 is 3.10+
source venv/bin/activate
pip install -r requirements.txt
```

## Running

From the repository root, with the virtualenv activated:

```bash
python client/test_client.py
```

To test a server script somewhere else, pass its path:

```bash
python client/test_client.py /path/to/other/server.py
```

The server is started with the **same Python interpreter** that runs the client, so it must be
able to import `mcp`. Use the virtualenv's Python and not the system one.

### Example output

```
Testing MCP server: /…/hello-py-mcp/server.py

[PASS] initialize -> server='hello-server'
[PASS] server declares tools capability
[PASS] ping
[PASS] tools/list includes 'hello' -> tools=['hello']
[PASS] 'hello' schema requires 'name' -> schema={...}
[PASS] call hello(name='Alice') -> 'Hello, Alice!'
[PASS] call hello() without name returns error
[PASS] call unknown tool returns error

All checks passed.
```

The server also writes log lines to stderr, which appear in your terminal, for example:

```
Tool 'hello' rejected arguments: ['name']
Tool 'does_not_exist' failed: 'Unknown tool: does_not_exist'
```

These come from checks 5 and 6 and are expected.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed |
| `1` | At least one check failed, the session could not start, or the server script was not found |

Because of these exit codes, the client works as a simple CI step or pre-commit check.

## Troubleshooting

- **`[FAIL] session aborted: MCPError: Connection closed`**: the server crashed during
  startup. Scroll up to see its traceback on stderr. A common cause is code written for SDK 1.x
  (for example `@server.list_tools()` or `from mcp.server.fastmcp import FastMCP`) running on
  `mcp` 2.x.
- **`ModuleNotFoundError: No module named 'mcp'`**: the virtualenv isn't active, or it was
  created with Python older than 3.10.
- **Interactive debugging**: to try tools by hand in a web UI, use the MCP Inspector instead:
  `npx @modelcontextprotocol/inspector python server.py`.
