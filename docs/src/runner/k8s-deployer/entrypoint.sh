#!/usr/bin/env bash
# k8s-deployer 容器启动入口。
set -euo pipefail

: "${GH_OWNER:?}"
: "${GH_REPO:?}"
: "${GH_RUNNER_TOKEN:?}"

RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,k8s-deployer}"
RUNNER_NAME="${RUNNER_NAME:-k8s-deployer-$(hostname)}"

cd /home/deployer/actions-runner

./config.sh --unattended \
  --url "https://github.com/${GH_OWNER}/${GH_REPO}" \
  --token "${GH_RUNNER_TOKEN}" \
  --name "${RUNNER_NAME}" \
  --labels "${RUNNER_LABELS}" \
  --work _work \
  --replace

trap 'echo "[entrypoint] removing runner"; ./config.sh remove --token "${GH_RUNNER_TOKEN}" || true' EXIT

exec ./run.sh
