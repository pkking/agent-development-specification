#!/usr/bin/env bash
# ai-dev-runner 容器启动入口。注册 self-hosted runner，然后开始监听 job。
set -euo pipefail

: "${GH_OWNER:?GH_OWNER required}"
: "${GH_REPO:?GH_REPO required}"
: "${GH_RUNNER_TOKEN:?GH_RUNNER_TOKEN required (registration token)}"

RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,ai-dev}"
RUNNER_NAME="${RUNNER_NAME:-ai-dev-$(hostname)}"

cd /home/runner/actions-runner

# Re-register on each start to refresh token
./config.sh --unattended \
  --url "https://github.com/${GH_OWNER}/${GH_REPO}" \
  --token "${GH_RUNNER_TOKEN}" \
  --name "${RUNNER_NAME}" \
  --labels "${RUNNER_LABELS}" \
  --work _work \
  --replace

trap 'echo "[entrypoint] removing runner"; ./config.sh remove --token "${GH_RUNNER_TOKEN}" || true' EXIT

exec ./run.sh
