# Rest Countries MCP Server

This project is a read-only MCP server that wraps the public Rest Countries API so Claude Code and other MCP clients can query country data through MCP tools.

## What it exposes

The server registers these MCP tools:

- `list_all_countries(fields: str)`
- `get_country_by_name(name: str)`
- `get_country_by_full_name(name: str)`
- `get_country_by_code(code: str)`
- `get_countries_by_codes(codes: str)`
- `get_countries_by_currency(currency: str)`
- `get_countries_by_language(language: str)`
- `get_countries_by_capital(capital: str)`
- `get_countries_by_region(region: str, fields: str | None = None)`
- `get_countries_by_subregion(subregion: str)`
- `get_countries_by_demonym(demonym: str)`
- `get_countries_by_translation(translation: str)`
- `get_countries_by_independent(status: bool, fields: str | None = None)`

All tools are read-only and return data from `https://restcountries.com`.

## Project layout

- `server.py`: the single MCP server entrypoint for Render and local HTTP runs
- `tools/countries.py`: Rest Countries tool implementations

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

- `RESTCOUNTRIES_BASE_URL`
- `REQUEST_TIMEOUT_SECONDS`
- `HOST`
- `PORT`
- `MCP_HTTP_PATH`
- `LOG_LEVEL`

## Claude Code MCP client setup

Use this after running locally or deploying the app to Render:

```bash
claude mcp add --transport http rest-countries https://<your-render-service>.onrender.com/mcp
```

Important: `https://restcountries.com` is not an MCP server. Your deployed Render app is the MCP server, and it calls Rest Countries internally.

## Render deployment

### Render blueprint

Create a Python web service in Render that runs `python server.py`.

### Manual Render settings

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `python server.py`
- Health check path: `/health`

### Expected environment variables

- `RESTCOUNTRIES_BASE_URL=https://restcountries.com`
- `REQUEST_TIMEOUT_SECONDS=10`
- `HOST=0.0.0.0`
- `MCP_HTTP_PATH=/mcp`
- `LOG_LEVEL=info`

Render will inject `PORT` automatically.

## Example prompts for testers

- "List all countries with only name and flags."
- "Find the country named eesti."
- "Find the country with full name Aruba."
- "Get the country with code col."
- "Find countries that use the currency cop."
- "List countries in the Europe region with only name and capital."
- "Find countries whose capital is Tallinn."
- "Find countries by translation alemania."

## Troubleshooting

- If Claude Code cannot connect to the remote server, verify the Render service URL and make sure the MCP endpoint path matches `/mcp`.
- If the service is up but tool calls fail, check the `/health` endpoint first and then review Render logs for upstream timeout or HTTP errors.
- If local HTTP does not appear in Claude Code, verify the server is running and that the URL points to `/mcp`.
- If you change the endpoint path with `MCP_HTTP_PATH`, update the Claude Code config to use the same path.
