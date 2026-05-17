"""提交变更计划分支 + 开/复用 PR（确定性）。

git 分支/add/commit/push（仅 issue_docs/<N>）+ gh pr create/list。
输出 PR_URL 到 GITHUB_ENV。
环境变量：ISSUE_NUMBER, ISSUE_TITLE, REPO_FULL, CHANGE_BRANCH
"""
from __future__ import annotations

import os
import sys

from release_lib import gh_api, run, set_env

ISSUE = os.environ["ISSUE_NUMBER"]
TITLE = os.environ.get("ISSUE_TITLE", "")
REPO = os.environ["REPO_FULL"]
BRANCH = os.environ["CHANGE_BRANCH"]

run(["git", "config", "user.name", "github-actions[bot]"])
run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
run(["git", "checkout", "-B", BRANCH])
run(["git", "add", "--", f"issue_docs/{ISSUE}"])

# 无改动则跳过（重跑产出相同）
staged = run(["git", "diff", "--cached", "--name-only"])
if not staged:
    print("::notice::变更计划无改动（重跑产出相同），跳过提交")
    sys.exit(0)

run(["git", "commit", "-m", f"docs: #{ISSUE} 变更计划说明书自动生成"])
run(["git", "push", "-u", "origin", BRANCH, "--force-with-lease"])

pr_url = run(
    ["gh", "pr", "list", "--repo", REPO, "--head", BRANCH,
     "--state", "open", "--json", "url", "-q", ".[0].url"],
    check=False,
)
if not pr_url or pr_url == "null":
    body = (
        f"自动生成的变更计划说明书。\n\nresolve #{ISSUE}\n\n"
        f"评审/补充后合入本 PR；之后由固定角色在 Issue #{ISSUE} 评论 `同意发布` 触发发布流水线。"
    )
    pr_url = run([
        "gh", "pr", "create", "--repo", REPO, "--base", "main",
        "--head", BRANCH,
        "--title", f"docs: #{ISSUE} {TITLE} change plan",
        "--body", body,
    ])

set_env("PR_URL", pr_url)
print(f"PR_URL={pr_url}")
