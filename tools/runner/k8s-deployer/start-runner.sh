#!/usr/bin/env bash
# 本地起单实例 k8s-deployer（调试用）。
set -euo pipefail

: "${GH_OWNER:?}"
: "${GH_REPO:?}"
: "${GH_RUNNER_TOKEN:?}"
: "${KUBECONFIG_FILE:?KUBECONFIG_FILE path required}"

IMAGE="${IMAGE:-k8s-deployer:latest}"
NAME="${NAME:-k8s-deployer-local}"

docker run -d --restart=unless-stopped \
  --name "${NAME}" \
  -e GH_OWNER="${GH_OWNER}" \
  -e GH_REPO="${GH_REPO}" \
  -e GH_RUNNER_TOKEN="${GH_RUNNER_TOKEN}" \
  -e RUNNER_LABELS="self-hosted,k8s-deployer" \
  -e KUBECONFIG=/home/deployer/.kube/config \
  -v "${KUBECONFIG_FILE}":/home/deployer/.kube/config:ro \
  "${IMAGE}"

docker logs -f "${NAME}"
