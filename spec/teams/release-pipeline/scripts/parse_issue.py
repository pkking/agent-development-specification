"""拉取 Issue 标题/正文/评论 → /tmp/opencode/issue.txt，并解析服务/版本/repo@tag。

确定性步骤（脚本化，替代 workflow 内联 bash），输出写 GITHUB_OUTPUT：
  service, version, repo_tags(JSON)
环境变量：ISSUE_NUMBER, REPO_FULL, ISSUE_TITLE
"""
from __future__ import annotations

import json
import os

from release_lib import gh_api, parse_issue_title, parse_repo_tags, set_output

ISSUE = os.environ["ISSUE_NUMBER"]
REPO = os.environ["REPO_FULL"]
TITLE = os.environ.get("ISSUE_TITLE", "")

body = gh_api(f"repos/{REPO}/issues/{ISSUE}", jq=".body // \"\"")
try:
    comments = gh_api(
        f"repos/{REPO}/issues/{ISSUE}/comments",
        jq='.[] | "- @\\(.user.login): \\(.body)"',
    )
except Exception:
    comments = ""

os.makedirs("/tmp/opencode", exist_ok=True)
with open("/tmp/opencode/issue.txt", "w", encoding="utf-8") as f:
    f.write(f"# Issue #{ISSUE}: {TITLE}\n\n## 正文\n{body}\n\n## 评论\n{comments}\n")

meta = parse_issue_title(TITLE)
repo_tags = parse_repo_tags(body)
set_output("service", meta["service"])
set_output("version", meta["version"])
set_output("repo_tags", json.dumps(repo_tags, ensure_ascii=False))

print(f"service={meta['service']} version={meta['version']} repo_tags={repo_tags}")
print("--- issue.txt (head) ---")
print("\n".join(open("/tmp/opencode/issue.txt", encoding="utf-8").read().splitlines()[:30]))
