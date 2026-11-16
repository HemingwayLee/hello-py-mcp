# MCP Test Client

A small MCP client that tests the hello server end to end. It works with both versions
of the server:

- **stdio** ([`../server.py`](../server.py), the default): it starts the server as a
  subprocess, the same way Claude Desktop and Claude Code do.
- **Streamable HTTP** ([`../http_server.py`](../http_server.py)): it connects to an
  already-running server by URL.

Either way, it runs the same series of protocol checks.

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

### Against the HTTP server (`http_server.py`)

Pass a URL instead of a file path. Any argument starting with `http://` or `https://` makes
the client connect over Streamable HTTP instead of starting a subprocess.

1. In one terminal, from the repository root, start the HTTP server and leave it running:

   ```bash
   venv/bin/python http_server.py
   ```

2. In a second terminal, from the repository root, run the client with the server's URL:

   ```bash
   venv/bin/python client/test_client.py http://127.0.0.1:1234/mcp
   ```

3. Stop the server with Ctrl+C when you're done.

The client doesn't start the server in this mode, so step 1 is required. To test a server on
another machine, use that machine's IP address in the URL (`http_server.py` listens on all
network interfaces).

The checks and the output are the same as for stdio, except the first line reads
`Testing MCP server over HTTP: http://127.0.0.1:1234/mcp`. The server's log lines (including
the expected errors from checks 5 and 6) appear in the **server's** terminal, not the
client's.

### Example output

```
Testing MCP server over stdio: /…/hello-py-mcp/server.py

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
| `1` | At least one check failed, the session could not start (including no server at the URL), or the server script was not found |

Because of these exit codes, the client works as a simple CI step or pre-commit check.

## Troubleshooting

- **`[FAIL] session aborted: MCPError: Connection closed`**: the server crashed during
  startup. Scroll up to see its traceback on stderr. A common cause is code written for SDK 1.x
  (for example `@server.list_tools()` or `from mcp.server.fastmcp import FastMCP`) running on
  `mcp` 2.x.
- **`[FAIL] session aborted: ConnectError: All connection attempts failed`** (HTTP mode):
  nothing is listening at that URL. Start `http_server.py` first, and check the port (`1234`)
  and the path (`/mcp`).
- **`ModuleNotFoundError: No module named 'mcp'`**: the virtualenv isn't active, or it was
  created with Python older than 3.10.
- **Interactive debugging**: to try tools by hand in a web UI, use the MCP Inspector instead:
  `npx @modelcontextprotocol/inspector python server.py`.
