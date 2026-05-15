"""Minimal GitHub API helper used by orchestrator / deployer.

Avoids heavy SDK deps; uses requests if available, else urllib.
Tokens are read from GITHUB_TOKEN env; never logged.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

API = "https://api.github.com"


def _token() -> str:
    t = os.environ.get("GITHUB_TOKEN")
    if not t:
        raise RuntimeError("GITHUB_TOKEN not set")
    return t


def request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{API}{path}" if path.startswith("/") else path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {_token()}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"github API {method} {path} failed: {e.code} {e.reason}") from e
    return json.loads(raw) if raw else {}


def comment_issue(owner: str, repo: str, issue_number: int, body: str) -> dict:
    return request("POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", {"body": body})


def create_pr(owner: str, repo: str, *, title: str, head: str, base: str, body: str) -> dict:
    return request(
        "POST",
        f"/repos/{owner}/{repo}/pulls",
        {"title": title, "head": head, "base": base, "body": body},
    )


def merge_pr(owner: str, repo: str, pr_number: int, *, method: str = "squash") -> dict:
    return request(
        "PUT",
        f"/repos/{owner}/{repo}/pulls/{pr_number}/merge",
        {"merge_method": method},
    )
