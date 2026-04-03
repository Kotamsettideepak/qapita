import os

from dotenv import load_dotenv


load_dotenv()


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


JSONPLACEHOLDER_BASE_URL = _get_required_env("JSONPLACEHOLDER_BASE_URL").rstrip("/")
REQUEST_TIMEOUT_SECONDS = float(_get_required_env("REQUEST_TIMEOUT_SECONDS"))
HTTP_HOST = _get_required_env("HOST")
HTTP_PORT = int(_get_required_env("PORT"))
MCP_HTTP_PATH = _get_required_env("MCP_HTTP_PATH")
LOG_LEVEL = _get_required_env("LOG_LEVEL")
