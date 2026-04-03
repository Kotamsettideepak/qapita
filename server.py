from __future__ import annotations

import asyncio

from fastmcp import FastMCP

from config import HTTP_HOST, HTTP_PORT, MCP_HTTP_PATH
from tools.countries import (
    get_countries_by_capital,
    get_countries_by_codes,
    get_countries_by_currency,
    get_countries_by_demonym,
    get_countries_by_independent,
    get_countries_by_language,
    get_countries_by_region,
    get_countries_by_subregion,
    get_countries_by_translation,
    get_country_by_code,
    get_country_by_full_name,
    get_country_by_name,
    list_all_countries,
)

mcp = FastMCP(
    "Rest Countries MCP Server",
    instructions="""
    Always use these tools when answering any question about countries.

    Do NOT rely on your own knowledge for country-related queries.
    Use the tools to fetch accurate and up-to-date data.
    """
)

mcp.tool()(list_all_countries)
mcp.tool()(get_country_by_name)
mcp.tool()(get_country_by_full_name)
mcp.tool()(get_country_by_code)
mcp.tool()(get_countries_by_codes)
mcp.tool()(get_countries_by_currency)
mcp.tool()(get_countries_by_language)
mcp.tool()(get_countries_by_capital)
mcp.tool()(get_countries_by_region)
mcp.tool()(get_countries_by_subregion)
mcp.tool()(get_countries_by_demonym)
mcp.tool()(get_countries_by_translation)
mcp.tool()(get_countries_by_independent)


app = mcp.http_app(path=MCP_HTTP_PATH, transport="http")


if __name__ == "__main__":
    asyncio.run(
        mcp.run_http_async(
            transport="http",
            host=HTTP_HOST,
            port=HTTP_PORT,
            path=MCP_HTTP_PATH,
            show_banner=False,
        )
    )
