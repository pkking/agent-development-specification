"""Thin wrapper around `kubectl` for the deployer.

Uses subprocess so we don't depend on python-kubernetes; relies on KUBECONFIG.
"""
from __future__ import annotations

import json
import subprocess


def apply(yaml_path: str, namespace: str) -> None:
    subprocess.run(
        ["kubectl", "apply", "-n", namespace, "-f", yaml_path],
        check=True,
    )


def delete(yaml_path: str, namespace: str) -> None:
    subprocess.run(
        ["kubectl", "delete", "-n", namespace, "-f", yaml_path, "--ignore-not-found=true"],
        check=False,
    )


def wait_ready(kind: str, name: str, namespace: str, timeout: str = "120s") -> None:
    subprocess.run(
        ["kubectl", "wait", f"--for=condition=Ready", f"{kind}/{name}",
         "-n", namespace, f"--timeout={timeout}"],
        check=True,
    )


def get(kind: str, name: str, namespace: str) -> dict:
    out = subprocess.run(
        ["kubectl", "get", f"{kind}/{name}", "-n", namespace, "-o", "json"],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)
