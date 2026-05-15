#!/usr/bin/env bash
# 本地起单实例 ai-dev-runner 容器（开发调试用）。
# 生产场景由 deployment.yaml 通过 K8s 拉起。
set -euo pipefail

: "${GH_OWNER:?}"
: "${GH_REPO:?}"
: "${GH_RUNNER_TOKEN:?}"

IMAGE="${IMAGE:-ai-dev-runner:latest}"
NAME="${NAME:-ai-dev-runner-local}"

docker run -d --restart=unless-stopped \
  --name "${NAME}" \
  -e GH_OWNER="${GH_OWNER}" \
  -e GH_REPO="${GH_REPO}" \
  -e GH_RUNNER_TOKEN="${GH_RUNNER_TOKEN}" \
  -e RUNNER_LABELS="self-hosted,ai-dev-runner" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
  -e ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-}" \
  -e ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-}" \
  -e GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
  "${IMAGE}"

echo "[start-runner] started container: ${NAME}"
docker logs -f "${NAME}"
