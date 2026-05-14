#!/usr/bin/env bash
# 构建 通用 AI 开发 runner 镜像并 push 到 SWR
# 待填: 完整实现

set -euo pipefail
IMAGE="swr.cn-southwest-2.myhuaweicloud.com/<org>/<<IMAGE_NAME>>:latest"
echo "[build] 待填: docker buildx build --platform linux/amd64,linux/arm64 --push -t $IMAGE ."
