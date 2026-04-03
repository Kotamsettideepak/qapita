from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import requests

from config import JSONPLACEHOLDER_BASE_URL, REQUEST_TIMEOUT_SECONDS


@dataclass
class APIError(Exception):
    error_type: str
    message: str
    status_code: int | None = None
    details: dict[str, Any] | None = None

    def to_response(self) -> dict[str, Any]:
        error: dict[str, Any] = {
            "ok": False,
            "error": {
                "type": self.error_type,
                "message": self.message,
            },
        }
        if self.status_code is not None:
            error["error"]["status_code"] = self.status_code
        if self.details:
            error["error"]["details"] = self.details
        return error


def _fetch_json(path: str, allow_404: bool = False) -> Any:
    url = f"{JSONPLACEHOLDER_BASE_URL}{path}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.Timeout as exc:
        raise APIError(
            error_type="upstream_timeout",
            message=f"Upstream request timed out after {REQUEST_TIMEOUT_SECONDS} seconds.",
            details={"url": url},
        ) from exc
    except requests.RequestException as exc:
        raise APIError(
            error_type="upstream_request_failed",
            message="Failed to reach the upstream API.",
            details={"url": url},
        ) from exc

    if allow_404 and response.status_code == 404:
        return None

    if response.status_code >= 400:
        raise APIError(
            error_type="upstream_http_error",
            message="Upstream API returned an error response.",
            status_code=response.status_code,
            details={"url": url, "response_text": response.text[:500]},
        )

    try:
        return response.json()
    except ValueError as exc:
        raise APIError(
            error_type="invalid_upstream_response",
            message="Upstream API returned invalid JSON.",
            status_code=response.status_code,
            details={"url": url},
        ) from exc


def _get_users() -> list[dict[str, Any]]:
    payload = _fetch_json("/users")
    if not isinstance(payload, list):
        raise APIError(
            error_type="invalid_upstream_response",
            message="Expected a list of users from the upstream API.",
        )
    return payload


def _get_user_by_id(user_id: int) -> dict[str, Any] | None:
    payload = _fetch_json(f"/users/{user_id}", allow_404=True)
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise APIError(
            error_type="invalid_upstream_response",
            message="Expected a user object from the upstream API.",
        )
    return payload


def _validate_user_id(user_id: int) -> int:
    if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id <= 0:
        raise ValueError("user_id must be a positive integer.")
    return user_id


def _normalize_query(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")
    return normalized.casefold()


def _filter_users(
    field_name: str,
    query: str,
    extractor: Callable[[dict[str, Any]], str | None],
) -> list[dict[str, Any]]:
    normalized_query = _normalize_query(query, field_name)
    try:
        users = _get_users()
    except APIError as exc:
        return [exc.to_response()]

    return [
        user
        for user in users
        if normalized_query in (extractor(user) or "").casefold()
    ]


def list_users() -> list[dict[str, Any]] | dict[str, Any]:
    """Return every user from the public JSONPlaceholder /users endpoint."""
    try:
        return _get_users()
    except APIError as exc:
        return exc.to_response()


def get_user_by_id(user_id: int) -> dict[str, Any]:
    """Return one user by numeric ID."""
    try:
        validated_user_id = _validate_user_id(user_id)
        user = _get_user_by_id(validated_user_id)
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }
    except APIError as exc:
        return exc.to_response()

    if user is None:
        return {
            "ok": False,
            "error": {
                "type": "not_found",
                "message": f"No user found with id {validated_user_id}.",
            },
        }
    return user


def search_users_by_name(name: str) -> list[dict[str, Any]] | dict[str, Any]:
    """Search users by name using case-insensitive substring matching."""
    try:
        return _filter_users("name", name, lambda user: user.get("name"))
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def search_users_by_username(username: str) -> list[dict[str, Any]] | dict[str, Any]:
    """Search users by username using case-insensitive substring matching."""
    try:
        return _filter_users("username", username, lambda user: user.get("username"))
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def search_users_by_email(email: str) -> list[dict[str, Any]] | dict[str, Any]:
    """Search users by email using case-insensitive substring matching."""
    try:
        return _filter_users("email", email, lambda user: user.get("email"))
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_user_contact_card(user_id: int) -> dict[str, Any]:
    """Return a compact contact card view for one user."""
    result = get_user_by_id(user_id)
    if result.get("ok") is False:
        return result

    company = result.get("company") or {}
    address = result.get("address") or {}
    geo = address.get("geo") or {}

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "username": result.get("username"),
        "email": result.get("email"),
        "phone": result.get("phone"),
        "website": result.get("website"),
        "company": company.get("name"),
        "city": address.get("city"),
        "street": address.get("street"),
        "suite": address.get("suite"),
        "zipcode": address.get("zipcode"),
        "geo": {
            "lat": geo.get("lat"),
            "lng": geo.get("lng"),
        },
    }
