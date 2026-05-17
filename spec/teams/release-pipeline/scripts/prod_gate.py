"""生产准入单项（真实）。用法：python prod_gate.py <gate>

gate ∈ branch-check | image-vuln-scan | virus-scan
工具缺失 → SKIP（不挡）；命中严重问题 → exit 1（fail-fast 停）。

环境变量：CONFIG_JSON, DRY_RUN, IMAGE_REF（build_image 的 set_env）
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

gate = sys.argv[1] if len(sys.argv) > 1 else ""
cfg = json.loads(os.environ.get("CONFIG_JSON", "{}"))
dry = os.environ.get("DRY_RUN", "true") == "true"


def which(*n):
    for x in n:
        if shutil.which(x):
            return x
    return None


if gate == "branch-check":
    br = cfg.get("default_branch", "main")
    # 发布分支规范：main / master / beta / release/* 允许；其它需显式放行
    if re.fullmatch(r"(main|master|beta|release/.+)", br):
        print(f"✓ branch-check: 发布分支 {br} 合规")
        sys.exit(0)
    print(f"::error::branch-check: 分支 {br} 不符合发布规范（要求 main/master/beta/release/*）")
    sys.exit(1)

elif gate == "image-vuln-scan":
    if dry:
        print("::notice::image-vuln-scan SKIP：演练态无真实镜像")
        sys.exit(0)
    ref = os.environ.get("IMAGE_REF", "")
    tv = which("trivy")
    if not ref:
        print("::error::image-vuln-scan: 无 IMAGE_REF（构建阶段未产出镜像）")
        sys.exit(1)
    if not tv:
        print("::notice::image-vuln-scan SKIP：runner 无 trivy（建议加入 runner 镜像）")
        sys.exit(0)
    r = subprocess.run([tv, "image", "--severity", "CRITICAL,HIGH",
                        "--exit-code", "1", "--ignore-unfixed", "--quiet", ref])
    if r.returncode != 0:
        print("::error::image-vuln-scan: 镜像含 CRITICAL/HIGH 漏洞")
        sys.exit(1)
    print(f"✓ image-vuln-scan: {ref} 通过")
    sys.exit(0)

elif gate == "virus-scan":
    if dry:
        print("::notice::virus-scan SKIP：演练态")
        sys.exit(0)
    cs = which("clamscan")
    if not cs:
        print("::notice::virus-scan SKIP：runner 无 clamav")
        sys.exit(0)
    target = "_src" if os.path.isdir("_src") else "."
    r = subprocess.run([cs, "-r", "--no-summary", "-i", target])
    if r.returncode == 1:
        print("::error::virus-scan: clamav 命中病毒")
        sys.exit(1)
    print("✓ virus-scan: clamav 未发现病毒")
    sys.exit(0)

else:
    print(f"::error::未知准入项：{gate}")
    sys.exit(1)
