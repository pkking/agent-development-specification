"""加载并校验 release-config/<service>.yaml，输出给通用发布流水线。

通用发布流水线（release.yml）= 一条流水线 + 每服务一份配置。
本脚本：按 service 名找配置 → 校验必填 → 规整默认值 → JSON 出到
GITHUB_OUTPUT 的 config 字段，供下游 job 用 fromJSON 消费。

环境变量：SERVICE（从 Issue 解析得到）
"""
from __future__ import annotations

import json
import os
import sys

try:
    import yaml
except ImportError:
    print("::error::缺少 pyyaml，请在 runner 上 pip install pyyaml")
    sys.exit(1)

from release_lib import set_output

SERVICE = os.environ.get("SERVICE", "").strip()
if not SERVICE:
    print("::error::未解析到服务名（SERVICE 为空）")
    sys.exit(1)

cfg_path = os.path.join("release-config", f"{SERVICE}.yaml")
if not os.path.isfile(cfg_path):
    print(f"::error::找不到服务配置 {cfg_path}。新增服务需在 release-config/ 下加 <service>.yaml")
    print("已存在的服务配置：" + ", ".join(
        sorted(f[:-5] for f in os.listdir("release-config") if f.endswith(".yaml"))
        if os.path.isdir("release-config") else []))
    sys.exit(1)

with open(cfg_path, encoding="utf-8") as f:
    cfg = yaml.safe_load(f) or {}

# ---- 必填校验 ----
required = ["service", "source_repo"]
missing = [k for k in required if not cfg.get(k)]
if missing:
    print(f"::error::{cfg_path} 缺必填字段：{missing}")
    sys.exit(1)

# ---- 默认值规整 ----
cfg.setdefault("default_branch", "main")
cfg.setdefault("dockerfile", "./Dockerfile")
cfg.setdefault("build_context", ".")
cfg.setdefault("build_args", {})

image = cfg.setdefault("image", {})
image.setdefault("mode", "local")            # local（k8s 集群内 registry，免华为云 SWR 凭据）| swr
image.setdefault("test_repo", "")
image.setdefault("prod_repo", "")
image.setdefault("local_registry", "")       # mode=local 时的集群内 registry（如 registry.ai-test.svc:5000/<svc>）

deploy = cfg.setdefault("deploy", {})
deploy.setdefault("mode", "none")            # kustomize | helm-value | none
deploy.setdefault("config_repo", "opensourceways/infra-common")
deploy.setdefault("config_branch", "main")
deploy.setdefault("test_path", "")
deploy.setdefault("prod_path", "")
deploy.setdefault("value_file", "value.yaml")
deploy.setdefault("image_tag_path", ".image.tag")

cfg.setdefault("health", {}).setdefault("url", "")

checks = cfg.setdefault("checks", {})
for k, v in {"sast": True, "vuln": True, "license": True, "ut": False,
             "image_scan": True, "virus_scan": False, "branch_check": True,
             # vuln_block=True：发现 CRITICAL/HIGH 即阻断发布（默认，严格）。
             # =False：仅告警不阻断——仅当变更计划已书面记录风险接受时由服务显式降级。
             "vuln_block": True}.items():
    checks.setdefault(k, v)

# image.mode=swr 时必须给 test/prod repo
if image["mode"] == "swr" and not (image["test_repo"] and image["prod_repo"]):
    print(f"::error::{cfg_path} image.mode=swr 但 test_repo/prod_repo 未填")
    sys.exit(1)

# ---- 配置驱动的矩阵（保证非空：含强制项）----
# 检查阶段：secret-scan + change-plan-integrity 强制；其余按 checks 开关
checks_matrix = ["secret-scan", "change-plan-integrity"]
for name, key in [("sast", "sast"), ("vuln-scan", "vuln"),
                  ("license-compliance", "license"), ("ut-coverage", "ut")]:
    if checks.get(key):
        checks_matrix.append(name)

# 生产准入：branch-check 强制（保证矩阵非空）；其余按开关
gates_matrix = ["branch-check"] if checks.get("branch_check", True) else []
if checks.get("image_scan"):
    gates_matrix.append("image-vuln-scan")
if checks.get("virus_scan"):
    gates_matrix.append("virus-scan")
if not gates_matrix:
    gates_matrix = ["branch-check"]

set_output("config", json.dumps(cfg, ensure_ascii=False))
set_output("checks_matrix", json.dumps(checks_matrix))
set_output("gates_matrix", json.dumps(gates_matrix))
# 常用字段单独出，方便 step 直接引用
set_output("source_repo", cfg["source_repo"])
set_output("image_mode", image["mode"])
set_output("deploy_mode", deploy["mode"])
print(f"✓ 已加载服务配置 {cfg_path}")
print(f"  checks_matrix={checks_matrix}")
print(f"  gates_matrix={gates_matrix}")
print(json.dumps(cfg, ensure_ascii=False, indent=2))
