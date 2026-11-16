# MCP HTML Client

[`index.html`](index.html) is an MCP client written in plain HTML and JavaScript, with no
libraries or build step. It connects to the hello server's HTTP version
([`../http_server.py`](../http_server.py)) from your browser, lists its tools, and calls
`hello`.

A **Protocol log** on the page shows every HTTP request and response, so you can see each
step of the protocol that tools like the MCP Inspector normally hide.

## Prerequisites

- The server's dependencies (Python 3.10+ and `mcp>=2`), set up from the repository root as
  described in the [main README](../README.md#installation).
- Any modern browser. Nothing needs to be installed for the page itself.

## Running

1. In a terminal, from the repository root, start the HTTP server and leave it running:

   ```bash
   venv/bin/python http_server.py
   ```

   It listens on port `1234`, and its MCP endpoint is `http://127.0.0.1:1234/mcp`.

2. Open `index.html` in your browser. Double-click it, or on macOS run:

   ```bash
   open http_client/index.html
   ```

   The page loads straight from disk (`file://…`); it doesn't need a web server.

3. Use the page:
   1. Check the URL (`http://127.0.0.1:1234/mcp` by default) and click **Connect**. The
      status line shows the server name, protocol version and session ID.
   2. Click **List Tools**. You should see `hello` and its `name` parameter.
   3. Enter a name and click **Run Tool** (or press Enter). The result is `Hello, Alice!`.
   4. Click **Disconnect** to end the session.

4. Stop the server with Ctrl+C when you're done.

To connect to a server on another machine, replace `127.0.0.1` with that machine's IP
address before clicking **Connect** (`http_server.py` listens on all network interfaces).

## What happens on the wire

These are the requests the page sends, as shown in the Protocol log:

| Step | Request | Server response |
|---|---|---|
| Connect | `POST /mcp` with `initialize` | Server info and protocol version, plus a new session ID in the `Mcp-Session-Id` header |
| Connect | `POST /mcp` with `notifications/initialized` | `202 Accepted`, no body (confirms the handshake) |
| List Tools | `POST /mcp` with `tools/list` | The tool names, descriptions and input schemas |
| Run Tool | `POST /mcp` with `tools/call` | The tool's result, e.g. `Hello, Alice!` |
| Disconnect | `DELETE /mcp` | `200 OK`; the server ends the session |

After the handshake, every request includes the `Mcp-Session-Id` and `MCP-Protocol-Version`
headers. The server answers in streaming format (`text/event-stream`), and the page reads the
JSON out of its `data:` lines.

## Why it works: CORS

A page opened from disk has the origin `null`, which is a different origin from
`http://127.0.0.1:1234`. Browsers block requests from a page to a different origin unless the
server explicitly allows them (CORS). `http_server.py` therefore:

- allows requests from any origin, including `null`, and
- **exposes the `Mcp-Session-Id` header.** Browsers hide response headers from JavaScript
  unless the server exposes them, and without the session ID the page can't continue after
  the handshake.

> **Note:** Because every origin is allowed, any web page open in your browser could call
> this server too. That's fine for this demo, but restrict `allow_origins` in
> `http_server.py` for anything real.

## Why it can't connect to `server.py`

`server.py` uses the **stdio** transport. It doesn't listen on any port; it reads requests
from its standard input and writes responses to its standard output. To use it, a client has
to **start it as a process** and hold those pipes, which is what Claude Code, Claude Desktop
and [`../client/test_client.py`](../client/test_client.py) do.

A web page can't do that. The browser sandbox doesn't let pages start programs or access a
process's stdin and stdout. If it did, any website you visit could run programs on your
computer. A page can only make network requests, so it needs a server that listens on a
network port, like `http_server.py`.

To reach a stdio server from a browser, you need a **bridge**: a program that starts
`server.py` over stdio and makes it available over HTTP.

```
index.html ──HTTP──► bridge ──stdio──► server.py
```

The bridge can't run inside the page either, for the same sandbox reason. It has to be a
separate program, for example:

- **`http_server.py`** (this repo): rather than bridging, it serves the same `hello` tool over
  HTTP directly. This is what `index.html` uses.
- **The MCP Inspector's proxy:** `npx @modelcontextprotocol/inspector python server.py`
  starts `server.py` and lets the Inspector's web page talk to it.
- **A standalone bridge** such as `supergateway` or `mcp-proxy`, or a small Node.js script.
  For `index.html` to use it, the bridge must also allow CORS and expose `Mcp-Session-Id`.

## Troubleshooting

- **"Could not reach the server (…)"** after clicking **Connect**: the browser couldn't
  complete the request. The text in parentheses depends on the browser (for example
  `Failed to fetch` in Chrome or `Load failed` in Safari). Check that:
  - `http_server.py` is running (not `server.py`), and the URL's port (`1234`) and path
    (`/mcp`) are correct;
  - the server is the current version with CORS enabled. Your browser's developer console
    (F12) shows a CORS error if it isn't.
- **`Bad Request: Missing session ID`** when you open `http://127.0.0.1:1234/mcp` directly in
  the browser: this is expected. The endpoint needs the MCP handshake first; use `index.html`
  or the MCP Inspector instead.
- **`Session not found (code -32600)` after the server restarted:** the server forgets its
  sessions when it stops, so the page's old session ID is no longer valid. Click
  **Disconnect**, then **Connect** again.
