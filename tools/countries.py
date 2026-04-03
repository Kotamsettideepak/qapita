from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import requests

from config import REQUEST_TIMEOUT_SECONDS, RESTCOUNTRIES_BASE_URL


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


def _validate_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")
    return normalized


def _optional_fields_query(fields: str | None) -> str:
    if fields is None:
        return ""
    normalized = _validate_text(fields, "fields")
    return f"?fields={quote(normalized, safe=',')}"


def _fetch_json(path: str, allow_404: bool = False) -> Any:
    url = f"{RESTCOUNTRIES_BASE_URL}{path}"
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
        return {
            "ok": False,
            "error": {
                "type": "not_found",
                "message": "No matching country data found.",
            },
        }

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


def _run_country_query(path: str, allow_404: bool = False) -> Any:
    try:
        return _fetch_json(path, allow_404=allow_404)
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }
    except APIError as exc:
        return exc.to_response()


def list_all_countries(fields: str) -> Any:
    """Return all countries. The fields parameter is required by this tool."""
    try:
        normalized_fields = _validate_text(fields, "fields")
        return _run_country_query(
            f"/v3.1/all?fields={quote(normalized_fields, safe=',')}"
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_country_by_name(name: str) -> Any:
    """Search by country name using common or official values."""
    try:
        normalized_name = _validate_text(name, "name")
        return _run_country_query(
            f"/v3.1/name/{quote(normalized_name)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_country_by_full_name(name: str) -> Any:
    """Search by the country's full name."""
    try:
        normalized_name = _validate_text(name, "name")
        return _run_country_query(
            f"/v3.1/name/{quote(normalized_name)}?fullText=true",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_country_by_code(code: str) -> Any:
    """Search by cca2, ccn3, cca3, or cioc country code."""
    try:
        normalized_code = _validate_text(code, "code")
        return _run_country_query(
            f"/v3.1/alpha/{quote(normalized_code)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_codes(codes: str) -> Any:
    """Search by multiple country codes separated by commas."""
    try:
        normalized_codes = _validate_text(codes, "codes")
        return _run_country_query(
            f"/v3.1/alpha?codes={quote(normalized_codes, safe=',')}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_currency(currency: str) -> Any:
    """Search by currency code or name."""
    try:
        normalized_currency = _validate_text(currency, "currency")
        return _run_country_query(
            f"/v3.1/currency/{quote(normalized_currency)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_language(language: str) -> Any:
    """Search by language code or language name."""
    try:
        normalized_language = _validate_text(language, "language")
        return _run_country_query(
            f"/v3.1/lang/{quote(normalized_language)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_capital(capital: str) -> Any:
    """Search by capital city."""
    try:
        normalized_capital = _validate_text(capital, "capital")
        return _run_country_query(
            f"/v3.1/capital/{quote(normalized_capital)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_region(region: str, fields: str | None = None) -> Any:
    """Filter countries by region, optionally limiting returned fields."""
    try:
        normalized_region = _validate_text(region, "region")
        return _run_country_query(
            f"/v3.1/region/{quote(normalized_region)}{_optional_fields_query(fields)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_subregion(subregion: str) -> Any:
    """Filter countries by subregion."""
    try:
        normalized_subregion = _validate_text(subregion, "subregion")
        return _run_country_query(
            f"/v3.1/subregion/{quote(normalized_subregion)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_demonym(demonym: str) -> Any:
    """Search by demonym."""
    try:
        normalized_demonym = _validate_text(demonym, "demonym")
        return _run_country_query(
            f"/v3.1/demonym/{quote(normalized_demonym)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_translation(translation: str) -> Any:
    """Search by translated country name."""
    try:
        normalized_translation = _validate_text(translation, "translation")
        return _run_country_query(
            f"/v3.1/translation/{quote(normalized_translation)}",
            allow_404=True,
        )
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }


def get_countries_by_independent(
    status: bool,
    fields: str | None = None,
) -> Any:
    """Return countries filtered by independence status."""
    if not isinstance(status, bool):
        return {
            "ok": False,
            "error": {
                "type": "validation_error",
                "message": "status must be a boolean value.",
            },
        }
    try:
        query = f"/v3.1/independent?status={'true' if status else 'false'}"
        if fields is not None:
            query += f"&fields={quote(_validate_text(fields, 'fields'), safe=',')}"
        return _run_country_query(query, allow_404=True)
    except ValueError as exc:
        return {
            "ok": False,
            "error": {"type": "validation_error", "message": str(exc)},
        }
