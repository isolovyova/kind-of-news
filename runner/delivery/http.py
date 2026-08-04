"""Minimal HTTP helpers used by delivery adapters."""

from __future__ import annotations

import json
from typing import Any, Dict, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import DeliveryError


def post_json(
    url: str,
    payload: Mapping[str, Any],
    headers: Optional[Mapping[str, str]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    request_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    request = Request(
        url,
        data=json.dumps(dict(payload), ensure_ascii=False).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise DeliveryError("remote service returned HTTP %s" % exc.code) from exc
    except URLError as exc:
        raise DeliveryError("remote service could not be reached") from exc
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return value if isinstance(value, dict) else {"value": value}


def post_text(
    url: str,
    text: str,
    headers: Optional[Mapping[str, str]] = None,
    timeout: int = 30,
) -> None:
    request_headers = {"Content-Type": "text/plain; charset=utf-8"}
    if headers:
        request_headers.update(headers)
    request = Request(url, data=text.encode("utf-8"), headers=request_headers, method="POST")
    try:
        with urlopen(request, timeout=timeout):
            return
    except HTTPError as exc:
        raise DeliveryError("remote service returned HTTP %s" % exc.code) from exc
    except URLError as exc:
        raise DeliveryError("remote service could not be reached") from exc
