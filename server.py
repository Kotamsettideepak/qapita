from __future__ import annotations

import asyncio

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from config import HTTP_HOST, HTTP_PORT, LOG_LEVEL, MCP_HTTP_PATH
from tools.users import (
    get_user_by_id,
    get_user_contact_card,
    list_users,
    search_users_by_email,
    search_users_by_name,
    search_users_by_username,
)

mcp = FastMCP(
    "JSONPlaceholder Users MCP Server",
    instructions=(
        "Use these tools to browse and search the public JSONPlaceholder users "
        "API. All tools are read-only and safe for testing."
    ),
)

mcp.tool()(list_users)
mcp.tool()(get_user_by_id)
mcp.tool()(search_users_by_name)
mcp.tool()(search_users_by_email)
mcp.tool()(search_users_by_username)
mcp.tool()(get_user_contact_card)


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def healthcheck(_request):
    return JSONResponse({"ok": True, "service": "jsonplaceholder-users-mcp"})


app = mcp.http_app(path=MCP_HTTP_PATH, transport="http")


if __name__ == "__main__":
    asyncio.run(
        mcp.run_http_async(
            transport="http",
            host=HTTP_HOST,
            port=HTTP_PORT,
            log_level=LOG_LEVEL,
            path=MCP_HTTP_PATH,
            show_banner=False,
        )
    )
