"""回评 Issue（确定性）。模式：success / fail / release_done / release_stop。

环境变量：ISSUE_NUMBER, REPO_FULL, GITHUB_RUN_ID
可选：PR_URL, DOC_DIR, MODE_TEXT, SERVICE, EXTRA
用法：python comment_issue.py <success|fail|release_done|release_stop>
"""
from __future__ import annotations

import os
import sys
import tempfile

from release_lib import run

ISSUE = os.environ["ISSUE_NUMBER"]
REPO = os.environ["REPO_FULL"]
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
RUN_URL = f"https://github.com/{REPO}/actions/runs/{RUN_ID}"
kind = sys.argv[1] if len(sys.argv) > 1 else "success"

if kind == "success":
    pr = os.environ.get("PR_URL", "")
    body = (
        "## 📋 变更计划说明书已生成\n\n"
        f"- 变更计划 PR：{pr}\n"
        f"- 路径：`issue_docs/{ISSUE}/Release/`\n"
        "- 评审/补充后**合入该 PR**。\n"
        "- 合入后，由**固定角色**在本 Issue 评论 `同意发布` 触发版本发布流水线（release.yml）。\n"
        "- 想重新生成：评论 `[重新生成变更计划]`。"
    )
elif kind == "fail":
    body = (
        f"❌ 变更计划自动生成异常，详见 [run logs]({RUN_URL})。"
        "修正 Issue 描述后评论 `[重新生成变更计划]` 重试。"
    )
elif kind == "release_done":
    mode = os.environ.get("MODE_TEXT", "演练")
    svc = os.environ.get("SERVICE", "")
    extra = os.environ.get("EXTRA", "")
    body = (
        f"## 🚀 发布流水线完成（{mode}）\n\n"
        f"- 服务：`{svc}`\n"
        f"- 变更计划：`issue_docs/{ISSUE}/Release/`（已校验存在）\n"
        f"- 阶段：鉴权 → 变更文档检查 → 检查项 → 构建部署测试 → 生产准入 → 部署生产\n"
        f"{extra}\n"
        f"- run: {RUN_URL}"
    )
elif kind == "release_stop":
    body = (
        f"⛔ 发布流水线某检查项失败，已停止后续步骤。详见 [run logs]({RUN_URL})。"
        "修复后重新评论 `同意发布` 重跑。"
    )
else:
    body = f"(unknown comment kind: {kind})"

with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
    tf.write(body)
    path = tf.name
run(["gh", "issue", "comment", ISSUE, "--repo", REPO, "--body-file", path], check=False)
print(f"commented ({kind}) on {REPO}#{ISSUE}")
