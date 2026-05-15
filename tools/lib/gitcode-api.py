"""Minimal GitCode API helper. Mirror of GitHub helper for parity."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

API = os.environ.get("GITCODE_API_BASE", "https://gitcode.com/api/v5")


def _token() -> str:
    t = os.environ.get("GITCODE_TOKEN")
    if not t:
        raise RuntimeError("GITCODE_TOKEN not set")
    return t


def request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{API}{path}" if path.startswith("/") else path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("PRIVATE-TOKEN", _token())
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"gitcode API {method} {path} failed: {e.code} {e.reason}") from e
    return json.loads(raw) if raw else {}


def comment_issue(owner: str, repo: str, issue_number: int, body: str) -> dict:
    return request(
        "POST",
        f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
        {"body": body},
    )
