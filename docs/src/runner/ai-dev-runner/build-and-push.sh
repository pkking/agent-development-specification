#!/usr/bin/env bash
# 构建 + 推送 ai-dev-runner 镜像。
set -euo pipefail

REGISTRY="${REGISTRY:?REGISTRY required, e.g. registry.example.com/team}"
IMAGE_NAME="${IMAGE_NAME:-ai-dev-runner}"
TAG="${TAG:-$(date +%Y%m%d-%H%M%S)}"
PLATFORMS="${PLATFORMS:-linux/amd64,linux/arm64}"

FULL="${REGISTRY}/${IMAGE_NAME}"

# 兼容旧 docker（无 buildx 时退到 docker build + push）
if docker buildx version >/dev/null 2>&1; then
  docker buildx build --platform "${PLATFORMS}" \
    -t "${FULL}:${TAG}" -t "${FULL}:latest" \
    --push .
else
  docker build -t "${FULL}:${TAG}" -t "${FULL}:latest" .
  docker push "${FULL}:${TAG}"
  docker push "${FULL}:latest"
fi

echo "[build-and-push] pushed ${FULL}:${TAG} and ${FULL}:latest"
