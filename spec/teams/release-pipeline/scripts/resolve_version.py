"""从被发布服务的源码仓现有 git tag 自动推算 next 版本号。

规则：取源码仓最新的 semver tag（vX.Y.Z），patch +1 作为本次发布版本；
      源码仓无任何 semver tag 时，首发版本 v0.0.1。
**不采信 Issue 标题里写的版本**（用户可能写错，如 APIMagic 已有 v1.0.0 却写 v0.0.1）。

输出到 GITHUB_OUTPUT：
  base_tag      源码仓当前最新 semver tag（无则空）
  next_version  本次应发布版本（base 的 patch+1，或 v0.0.1）

环境变量：CONFIG_JSON（含 source_repo）；SOURCE_REPO_TOKEN 优先，回退 GH_TOKEN
（源码仓多为私有，需能读其 tag 的 token）。
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

from release_lib import set_output

cfg = json.loads(os.environ["CONFIG_JSON"])
repo = cfg["source_repo"]
tok = os.environ.get("SOURCE_REPO_TOKEN") or os.environ.get("GH_TOKEN", "")

req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/tags?per_page=100",
    headers={"Authorization": f"token {tok}", "User-Agent": "rm",
             "Accept": "application/vnd.github+json"})
try:
    with urllib.request.urlopen(req) as r:
        tags = json.load(r)
except Exception as e:
    print(f"::error::读取 {repo} tags 失败（检查 SOURCE_REPO_TOKEN 是否能读该私有仓）：{e}")
    sys.exit(1)

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
vers = []
for t in (tags if isinstance(tags, list) else []):
    m = SEMVER.match(t.get("name", ""))
    if m:
        vers.append((tuple(int(x) for x in m.groups()), t["name"]))

if vers:
    vers.sort()
    (maj, mnr, pat), base = vers[-1]
    next_version = f"v{maj}.{mnr}.{pat + 1}"
else:
    base = ""
    next_version = "v0.0.1"

set_output("base_tag", base)
set_output("next_version", next_version)
print(f"源码仓 {repo} 现有 semver tag: {[v[1] for v in vers] or '无'}")
print(f"base_tag={base or '(无)'}  ->  next_version={next_version}")
