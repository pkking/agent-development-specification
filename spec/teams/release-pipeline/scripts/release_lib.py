"""release-mgmt 自动化共享库（确定性逻辑，纯脚本，不依赖 AI）。

提供：命令执行、gh api 封装、敏感信息扫描、GITHUB_OUTPUT/ENV 写入、
issue 标题解析（服务名/版本/repo@tag）。被 workflow_change / release 的
各脚本复用，集中维护提升稳定性与可测性。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

# 敏感信息正则（与各仓铁规一致；命中即判失败，绝不提交/发布）
SENSITIVE_PATTERNS = [
    r"ghp_[A-Za-z0-9]{15,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[A-Z0-9]{16}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"""password\s*[:=]\s*["'][^"']{6,}""",
    r"jdbc:[a-z]+:[^\s]*://[^\s]*:[^\s]*@",
]
_SENS_RE = re.compile("|".join(SENSITIVE_PATTERNS))


def run(cmd: list[str], check: bool = True, capture: bool = True, cwd: str | None = None) -> str:
    """跑命令，返回 stdout（strip）。check=True 时非 0 抛错。"""
    r = subprocess.run(
        cmd, cwd=cwd, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    out = (r.stdout or "").strip() if capture else ""
    if check and r.returncode != 0:
        raise RuntimeError(f"命令失败({r.returncode}): {' '.join(cmd)}\n{out}")
    return out


def gh_api(path: str, jq: str | None = None, method: str | None = None,
           fields: dict | None = None) -> str:
    """调 gh api。fields 走 -f key=value。"""
    cmd = ["gh", "api", path]
    if method:
        cmd += ["-X", method]
    for k, v in (fields or {}).items():
        cmd += ["-f", f"{k}={v}"]
    if jq:
        cmd += ["--jq", jq]
    return run(cmd)


def scan_sensitive(root: str) -> list[str]:
    """递归扫描 root 下文本文件，返回命中行（文件:行: 内容）。空=干净。"""
    hits: list[str] = []
    for dirpath, _dirs, files in os.walk(root):
        if "/.git" in dirpath.replace("\\", "/"):
            continue
        for fn in files:
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if _SENS_RE.search(line):
                            hits.append(f"{fp}:{i}: {line.strip()[:120]}")
            except OSError:
                continue
    return hits


def set_output(key: str, value: str) -> None:
    """写 GITHUB_OUTPUT（多行用 heredoc 风格）。"""
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if not gh_out:
        print(f"[output] {key}={value}")
        return
    with open(gh_out, "a", encoding="utf-8") as f:
        if "\n" in value:
            f.write(f"{key}<<__EOF__\n{value}\n__EOF__\n")
        else:
            f.write(f"{key}={value}\n")


def set_env(key: str, value: str) -> None:
    gh_env = os.environ.get("GITHUB_ENV")
    if not gh_env:
        print(f"[env] {key}={value}")
        return
    with open(gh_env, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")


def parse_issue_title(title: str) -> dict:
    """从 Issue 标题解析 服务名 / 版本号。与具体服务解耦。

    支持："发布 APIMagic 服务 v1.0.0 到今天的变更发布" / "发布APIMagic服务到今天为止的变更"
         / "om-dataarts v1.0.0 版本发布" / "APIMagic v1.0.0 后续变更发布"
    """
    title = title or ""
    service = ""
    m = re.search(r"发布[ 　]*([A-Za-z0-9_.\-]+)", title)
    if m:
        service = m.group(1)
    if not service:
        m = re.match(r"^([A-Za-z0-9_.\-]+)[ 　]", title)
        if m:
            service = m.group(1)
    if not service:
        service = "unknown-service"
    vm = re.search(r"v\d+\.\d+\.\d+", title)
    version = vm.group(0) if vm else ""
    return {"service": service, "version": version}


def parse_repo_tags(body: str) -> list[dict]:
    """从 Issue 正文「比较基准」表或 `repo@tag` 文本提取 repo@tag 对。"""
    pairs: list[dict] = []
    if not body:
        return pairs
    # 形如 owner/repo@v1.2.0 或 repo@v1.2.0
    for m in re.finditer(r"([A-Za-z0-9_.\-/]+)@(v?[\w.\-]+)", body):
        pairs.append({"repo": m.group(1), "tag": m.group(2)})
    # 去重
    seen = set()
    uniq = []
    for p in pairs:
        k = (p["repo"], p["tag"])
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


if __name__ == "__main__":
    # 自测
    for t in ["发布 APIMagic 服务 v1.0.0 到今天的变更发布",
              "发布APIMagic服务到今天为止的变更",
              "om-dataarts v1.0.0 版本发布"]:
        print(t, "->", json.dumps(parse_issue_title(t), ensure_ascii=False))
