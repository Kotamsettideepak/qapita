import os

from dotenv import load_dotenv


load_dotenv()


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


RESTCOUNTRIES_BASE_URL = _get_required_env("RESTCOUNTRIES_BASE_URL").rstrip("/")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
HTTP_HOST = os.getenv("HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("PORT", "8000"))
MCP_HTTP_PATH = os.getenv("MCP_HTTP_PATH", "/mcp")
