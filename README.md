# JSONPlaceholder Users MCP Server

This project is a read-only MCP server that wraps the public JSONPlaceholder `/users` API so Claude Code and other MCP clients can test against a simple, public dataset.

## What it exposes

The server registers these MCP tools:

- `list_users()`
- `get_user_by_id(user_id: int)`
- `search_users_by_name(name: str)`
- `search_users_by_email(email: str)`
- `search_users_by_username(username: str)`
- `get_user_contact_card(user_id: int)`

All search tools use case-insensitive substring matching against the `/users` response. All tools are read-only.

## Project layout

- `server.py`: the single MCP server entrypoint for Render and local HTTP runs
- `tools/users.py`: read-only users tool implementations

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python server.py
```

Default local URLs:

- MCP endpoint: `http://127.0.0.1:8000/mcp`
- Health endpoint: `http://127.0.0.1:8000/health`

You can customize the server with environment variables:

- `JSONPLACEHOLDER_BASE_URL` default: `https://jsonplaceholder.typicode.com`
- `REQUEST_TIMEOUT_SECONDS` default: `10`
- `HOST` default: `0.0.0.0`
- `PORT` default: `8000`
- `MCP_HTTP_PATH` default: `/mcp`
- `LOG_LEVEL` default: `info`

## Claude Code MCP client setup

Use this after running locally or deploying the app to Render:

```bash
claude mcp add --transport http jsonplaceholder-users https://<your-render-service>.onrender.com/mcp
```

Important: `https://jsonplaceholder.typicode.com/users` is not an MCP server. Your deployed Render app is the MCP server, and it calls JSONPlaceholder internally.

## Render deployment

### Render blueprint

This repo includes `render.yaml`, which configures a Python web service.

### Manual Render settings

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `python server.py`
- Health check path: `/health`

### Expected environment variables

- `JSONPLACEHOLDER_BASE_URL=https://jsonplaceholder.typicode.com`
- `REQUEST_TIMEOUT_SECONDS=10`
- `MCP_HTTP_PATH=/mcp`
- `LOG_LEVEL=info`

Render will inject `PORT` automatically.

## Example prompts for testers

- "List all users from the JSONPlaceholder MCP server."
- "Find the user with id 3."
- "Search for users whose username contains Bret."
- "Get the contact card for the user named Leanne Graham."
- "Find users whose email contains april.biz."

## Troubleshooting

- If Claude Code cannot connect to the remote server, verify the Render service URL and make sure the MCP endpoint path matches `/mcp`.
- If the service is up but tool calls fail, check the `/health` endpoint first and then review Render logs for upstream timeout or HTTP errors.
- If local HTTP does not appear in Claude Code, verify the server is running and that the URL points to `/mcp`.
- If you change the endpoint path with `MCP_HTTP_PATH`, update the Claude Code config to use the same path.
