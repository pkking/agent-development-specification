"""真实镜像构建（配置驱动）。

image.mode=local：用 containerd 工具链构建并导入 k8s.io 命名空间
  —— 优先 `nerdctl --namespace k8s.io build`（构建产物直接进 k8s.io，无需再 import）
  —— 退化 `buildah bud` + `ctr -n k8s.io images import`
  —— 退化 `ctr` 仅在有 image tar 时 import
  不需要华为云 SWR 凭据。
image.mode=swr：docker/nerdctl login 华为云 SWR → build → push（需 SWR_* secret）。

源码来自 source_repo（被发布服务的仓），按 default_branch checkout 到 ./_src。

环境变量：
  CONFIG_JSON  服务配置(JSON, resolve 输出)
  DRY_RUN      true/false
  GH_TOKEN     clone 源码仓用
  IMAGE_TAG    镜像 tag（默认 时间戳-shortsha）
  SWR_TEST_REGISTRY_USER/PASSWORD（mode=swr 测试）
退出码非 0 → 整条流水线 fail-fast 停。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time

from release_lib import run, set_env, set_output

cfg = json.loads(os.environ["CONFIG_JSON"])
dry = os.environ.get("DRY_RUN", "true") == "true"
svc = cfg["service"]
src_repo = cfg["source_repo"]
branch = cfg.get("default_branch", "main")
dockerfile = cfg.get("dockerfile", "./Dockerfile")
ctx = cfg.get("build_context", ".")
build_args = cfg.get("build_args", {})
image = cfg["image"]
mode = image["mode"]
tag = os.environ.get("IMAGE_TAG") or time.strftime("%Y%m%d-%H%M%S")

SRC = "_src"


def which(*names: str) -> str | None:
    for n in names:
        if shutil.which(n):
            return n
    return None


def build_arg_flags() -> list[str]:
    out = []
    for k, v in build_args.items():
        out += ["--build-arg", f"{k}={v}"]
    return out


def clone_src() -> None:
    if os.path.isdir(SRC):
        shutil.rmtree(SRC, ignore_errors=True)
    tok = os.environ.get("SOURCE_REPO_TOKEN") or os.environ.get("GH_TOKEN", "")
    url = f"https://x-access-token:{tok}@github.com/{src_repo}.git" if tok else f"https://github.com/{src_repo}.git"
    # token 只用于 clone，不回显（subprocess 不打印 url）
    subprocess.run(["git", "clone", "--depth", "1", "--branch", branch, url, SRC],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    print(f"✓ 已 clone {src_repo}@{branch} → {SRC}/")


def main() -> int:
    if mode == "local":
        local_ref = f"{(image.get('local_registry') or svc).rstrip('/')}:{tag}"
        set_output("image_ref", local_ref)
        set_env("IMAGE_REF", local_ref)
        if dry:
            print(f"::notice::[演练] image.mode=local —— 跳过真实构建。"
                  f"正式时：clone {src_repo}@{branch} → 构建 {dockerfile} → 导入 k8s.io containerd，镜像 {local_ref}")
            return 0
        clone_src()
        nerdctl = which("nerdctl")
        if nerdctl:
            # nerdctl --namespace k8s.io：构建产物直接落 k8s.io，kubelet 可直接用，无需 import
            cmd = [nerdctl, "--namespace", "k8s.io", "build",
                   "-t", local_ref, "-f", os.path.join(SRC, dockerfile.lstrip("./")),
                   *build_arg_flags(), os.path.join(SRC, ctx)]
            run(cmd, capture=False)
            print(f"✓ nerdctl 构建并落入 k8s.io: {local_ref}")
            return 0
        buildah = which("buildah")
        ctr = which("ctr")
        if buildah and ctr:
            run([buildah, "bud", "-t", local_ref, "-f",
                 os.path.join(SRC, dockerfile.lstrip("./")),
                 *build_arg_flags(), os.path.join(SRC, ctx)], capture=False)
            run([buildah, "push", local_ref, f"oci-archive:/tmp/{svc}.tar:{local_ref}"], capture=False)
            run([ctr, "-n", "k8s.io", "images", "import", f"/tmp/{svc}.tar"], capture=False)
            print(f"✓ buildah 构建 + ctr 导入 k8s.io: {local_ref}")
            return 0
        print("::error::image.mode=local 需要 containerd 构建工具链。当前 runner 无 nerdctl / (buildah+ctr)。")
        print("::error::运维需在 ai-dev-runner 上二选一：")
        print("::error::  A) 装 nerdctl 并挂载 /run/containerd/containerd.sock（推荐，--namespace k8s.io build 一步到位）")
        print("::error::  B) 装 buildah + ctr，并挂载 containerd sock（buildah bud → ctr -n k8s.io images import）")
        return 1

    # mode == swr
    test_repo = image.get("test_repo", "")
    swr_ref = f"{test_repo}:{tag}"
    set_output("image_ref", swr_ref)
    set_env("IMAGE_REF", swr_ref)
    if dry:
        print(f"::notice::[演练] image.mode=swr —— 跳过真实构建/推送。正式时：登录 SWR → 构建 → 推 {swr_ref}")
        return 0
    clone_src()
    builder = which("nerdctl", "docker")
    if not builder:
        print("::error::image.mode=swr 需要 docker 或 nerdctl，当前 runner 都没有")
        return 1
    reg = test_repo.split("/")[0]
    user = os.environ.get("SWR_TEST_REGISTRY_USER", "")
    pw = os.environ.get("SWR_TEST_REGISTRY_PASSWORD", "")
    if not (user and pw):
        print("::error::image.mode=swr 但未配 SWR_TEST_REGISTRY_USER/PASSWORD")
        return 1
    # --password-stdin：密码不进命令行/日志
    p = subprocess.run([builder, "login", reg, "-u", user, "--password-stdin"],
                       input=pw, text=True)
    if p.returncode != 0:
        print("::error::SWR 登录失败")
        return 1
    run([builder, "build", "-t", swr_ref, "-f",
         os.path.join(SRC, dockerfile.lstrip("./")),
         *build_arg_flags(), os.path.join(SRC, ctx)], capture=False)
    run([builder, "push", swr_ref], capture=False)
    print(f"✓ 构建并推送 SWR: {swr_ref}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
