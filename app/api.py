"""Thin client for the FatSecret Platform API (OAuth 2.0 client credentials)."""
import time
from typing import Optional

import requests

from app import config


class FatSecretError(Exception):
    """Raised when FatSecret cannot be reached or returns an error."""


_token: Optional[str] = None
_token_expires_at: float = 0.0


def get_access_token() -> str:
    """Return a cached OAuth 2.0 access token, fetching a new one when it expires."""
    global _token, _token_expires_at

    if _token and time.time() < _token_expires_at:
        return _token

    if not config.FATSECRET_CLIENT_ID or not config.FATSECRET_CLIENT_SECRET:
        raise FatSecretError(
            "FATSECRET_CLIENT_ID and FATSECRET_CLIENT_SECRET must be set (see .env.example)"
        )

    try:
        response = requests.post(
            config.TOKEN_URL,
            auth=(config.FATSECRET_CLIENT_ID, config.FATSECRET_CLIENT_SECRET),
            data={"grant_type": "client_credentials", "scope": "basic"},
            timeout=config.REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise FatSecretError(f"Could not reach FatSecret token endpoint: {exc}") from exc

    if response.status_code != 200:
        raise FatSecretError(f"Failed to obtain access token (HTTP {response.status_code})")

    payload = response.json()
    _token = payload["access_token"]
    # Refresh a minute early to avoid using a token right as it expires.
    _token_expires_at = time.time() + int(payload.get("expires_in", 3600)) - 60
    return _token


def search_foods(query: str, page_number: int = 0, max_results: int = 20) -> dict:
    """Call FatSecret `foods.search` and return the raw `foods` object."""
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    params = {
        "method": "foods.search",
        "format": "json",
        "search_expression": query,
        "page_number": page_number,
        "max_results": max_results,
    }
    try:
        response = requests.get(
            config.API_URL, headers=headers, params=params, timeout=config.REQUEST_TIMEOUT
        )
    except requests.RequestException as exc:
        raise FatSecretError(f"Could not reach FatSecret API: {exc}") from exc

    if response.status_code != 200:
        raise FatSecretError(f"FatSecret API returned HTTP {response.status_code}")

    body = response.json()
    # FatSecret reports errors (bad credentials, IP not whitelisted, ...) with HTTP 200.
    if "error" in body:
        error = body["error"]
        raise FatSecretError(f"FatSecret error {error.get('code')}: {error.get('message')}")

    return body.get("foods", {})
