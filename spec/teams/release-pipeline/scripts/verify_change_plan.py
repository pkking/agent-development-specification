"""校验变更计划产物 + 敏感扫描（确定性硬门禁）。

- issue_docs/<N>/Release/ 下必须有 .md
- 该目录敏感扫描命中即 exit 1（绝不提交）
环境变量：ISSUE_NUMBER
"""
from __future__ import annotations

import glob
import os
import sys

from release_lib import scan_sensitive, set_output

ISSUE = os.environ["ISSUE_NUMBER"]
doc_dir = f"issue_docs/{ISSUE}/Release"

mds = glob.glob(os.path.join(doc_dir, "*.md"))
if not mds:
    print(f"::error::变更计划未生成（{doc_dir} 下无 .md），opencode 输出可能为空")
    sys.exit(1)

hits = scan_sensitive(f"issue_docs/{ISSUE}")
if hits:
    print("::error::变更计划命中敏感信息，已阻止提交：")
    for h in hits[:20]:
        print("  " + h)
    sys.exit(1)

set_output("doc_dir", doc_dir)
print(f"✓ 变更计划已生成且无敏感信息：{mds}")
