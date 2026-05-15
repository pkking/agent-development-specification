#!/usr/bin/env bash
set -euo pipefail

REGISTRY="${REGISTRY:?}"
IMAGE_NAME="${IMAGE_NAME:-k8s-deployer}"
TAG="${TAG:-$(date +%Y%m%d-%H%M%S)}"
PLATFORMS="${PLATFORMS:-linux/amd64,linux/arm64}"

FULL="${REGISTRY}/${IMAGE_NAME}"

if docker buildx version >/dev/null 2>&1; then
  docker buildx build --platform "${PLATFORMS}" -t "${FULL}:${TAG}" -t "${FULL}:latest" --push .
else
  docker build -t "${FULL}:${TAG}" -t "${FULL}:latest" .
  docker push "${FULL}:${TAG}"
  docker push "${FULL}:latest"
fi
