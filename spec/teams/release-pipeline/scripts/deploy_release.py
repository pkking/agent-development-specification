"""部署（真实，配置驱动）。用法：python deploy_release.py <test|prod>

deploy.mode:
  none        ：镜像已构建/导入集群，不动部署仓（本地 k8s 测试足够）→ 直接通过
  kustomize   ：clone config_repo → cd <env path> → kustomize edit set image → commit/push
  helm-value  ：clone config_repo → 改 <env path>/<value_file> 的 <image_tag_path> → commit/push
config_repo 改动 → ArgoCD 监听同步到对应环境。

环境变量：CONFIG_JSON, DRY_RUN, IMAGE_REF, IMAGE_TAG,
          INFRA_COMMON_REPO_TOKEN（无则回退 RELEASE_MGMT_TOKEN / GH_TOKEN）
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

from release_lib import run

env_kind = sys.argv[1] if len(sys.argv) > 1 else "test"
cfg = json.loads(os.environ["CONFIG_JSON"])
dry = os.environ.get("DRY_RUN", "true") == "true"
dep = cfg["deploy"]
mode = dep.get("mode", "none")
tag = os.environ.get("IMAGE_TAG", "")
image_ref = os.environ.get("IMAGE_REF", "")
CFG_DIR = "_infra_common"


def tok() -> str:
    return (os.environ.get("INFRA_COMMON_REPO_TOKEN")
            or os.environ.get("RELEASE_MGMT_TOKEN")
            or os.environ.get("GH_TOKEN", ""))


if mode == "none":
    print(f"✓ deploy[{env_kind}]: deploy.mode=none，镜像已在集群内，无部署仓改动")
    sys.exit(0)

path = dep.get("test_path") if env_kind == "test" else dep.get("prod_path")
if not path:
    print(f"::error::deploy[{env_kind}]: deploy.mode={mode} 但 {env_kind}_path 未配")
    sys.exit(1)

if dry:
    print(f"::notice::[演练] deploy[{env_kind}] mode={mode}：将改 {dep['config_repo']}/{path} "
          f"的镜像 tag 为 {tag}（演练不真改）")
    sys.exit(0)

if shutil.which("git") is None:
    print("::error::无 git")
    sys.exit(1)
if os.path.isdir(CFG_DIR):
    shutil.rmtree(CFG_DIR, ignore_errors=True)
url = f"https://x-access-token:{tok()}@github.com/{dep['config_repo']}.git"
subprocess.run(["git", "clone", "--depth", "1", "--branch",
                dep.get("config_branch", "main"), url, CFG_DIR],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
run(["git", "-C", CFG_DIR, "config", "user.name", "release-bot"])
run(["git", "-C", CFG_DIR, "config", "user.email", "release-bot@users.noreply.github.com"])

workdir = os.path.join(CFG_DIR, path)
if not os.path.isdir(workdir):
    print(f"::error::部署仓中不存在路径 {path}")
    sys.exit(1)

if mode == "kustomize":
    if shutil.which("kustomize") is None:
        print("::error::deploy.mode=kustomize 但 runner 无 kustomize")
        sys.exit(1)
    base = image_ref.rsplit(":", 1)[0]
    run(["kustomize", "edit", "set", "image", f"{base}={image_ref}"], cwd=workdir, capture=False)
elif mode == "helm-value":
    if shutil.which("yq") is None:
        print("::error::deploy.mode=helm-value 但 runner 无 yq")
        sys.exit(1)
    vf = os.path.join(workdir, dep.get("value_file", "value.yaml"))
    tp = dep.get("image_tag_path", ".image.tag")
    run(["yq", "-i", f'{tp} = "{tag}"', vf], capture=False)
else:
    print(f"::error::未知 deploy.mode={mode}")
    sys.exit(1)

st = run(["git", "-C", CFG_DIR, "status", "--porcelain"])
if not st:
    print(f"::notice::deploy[{env_kind}]: 部署仓无变化，跳过提交")
    sys.exit(0)
run(["git", "-C", CFG_DIR, "add", "-A"])
run(["git", "-C", CFG_DIR, "commit", "-m",
     f"release: {cfg['service']} {env_kind} → {tag}"])
run(["git", "-C", CFG_DIR, "push", "origin", dep.get("config_branch", "main")])
print(f"✓ deploy[{env_kind}]: 已更新 {dep['config_repo']}/{path} 镜像 tag={tag}，ArgoCD 将同步")
