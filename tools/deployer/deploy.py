#!/usr/bin/env python3
"""k8s-deployer entrypoint — render templates by deploy_mode + kubectl apply.

Inputs are passed as CLI flags. See ../../docs/pipeline/generic-layer/deployer.md
for full contract.
"""
from __future__ import annotations

import argparse
import os
import string
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES = SCRIPT_DIR / "templates"


def render(template_dir: Path, vars_: dict[str, str], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    for tpl in sorted(template_dir.glob("*.yaml")):
        text = tpl.read_text(encoding="utf-8")
        text = string.Template(text).safe_substitute(vars_)
        dst = out_dir / tpl.name
        dst.write_text(text, encoding="utf-8")
        rendered.append(dst)
    return rendered


def kubectl_apply(files: list[Path], namespace: str) -> None:
    for f in files:
        subprocess.run(
            ["kubectl", "apply", "-n", namespace, "-f", str(f)],
            check=True,
        )


def kubectl_delete(files: list[Path], namespace: str) -> None:
    for f in files:
        subprocess.run(
            ["kubectl", "delete", "-n", namespace, "-f", str(f), "--ignore-not-found=true"],
            check=False,
        )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--service", required=True)
    p.add_argument("--mode", required=True, choices=["dev-pod", "data-pod", "shared", "none"])
    p.add_argument("--image", required=True, help="full image ref incl. registry/repo/tag")
    p.add_argument("--pr-number", required=True)
    p.add_argument("--namespace", required=True)
    p.add_argument("--base-domain", default=os.environ.get("BASE_DOMAIN", ""))
    p.add_argument("--cleanup", action="store_true", help="delete instead of apply")
    args = p.parse_args()

    if args.mode == "none":
        print("[deploy] mode=none, nothing to do")
        return 0

    template_dir = TEMPLATES / args.mode
    if not template_dir.is_dir():
        print(f"[deploy] ERROR: template dir not found: {template_dir}", file=sys.stderr)
        return 2

    out_dir = SCRIPT_DIR / ".rendered" / f"{args.project}-{args.service}-pr{args.pr_number}"

    vars_ = {
        "PROJECT": args.project,
        "SERVICE": args.service,
        "PR_NUMBER": args.pr_number,
        "IMAGE_FULL": args.image,
        "NAMESPACE": args.namespace,
        "BASE_DOMAIN": args.base_domain,
    }

    files = render(template_dir, vars_, out_dir)
    if args.cleanup:
        kubectl_delete(files, args.namespace)
        print(f"[deploy] cleaned up {len(files)} resources")
    else:
        kubectl_apply(files, args.namespace)
        print(f"[deploy] applied {len(files)} resources to namespace={args.namespace}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
