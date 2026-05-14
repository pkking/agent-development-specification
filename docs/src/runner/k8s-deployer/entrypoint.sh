#!/usr/bin/env bash
# k8s-deployer 容器启动入口。注册 self-hosted runner，然后开始监听 job。
#
# 依赖说明 — 本脚本调用的 `./config.sh` 和 `./run.sh` **不在本仓**，由 Dockerfile 在镜像构建期下载 actions-runner
# tar.gz 并 `tar xzf` 到 /home/deployer/actions-runner/ 提供。Dockerfile 相关段：
#
#   RUN mkdir -p /home/deployer/actions-runner && cd /home/deployer/actions-runner \
#       && curl -fsSL -o runner.tar.gz \
#          "https://github.com/actions/runner/releases/download/v${GH_RUNNER_VERSION}/actions-runner-linux-${TARGETARCH}-${GH_RUNNER_VERSION}.tar.gz" \
#       && tar xzf runner.tar.gz && rm runner.tar.gz
#
# 如果你跑 entrypoint 时报「config.sh: No such file」，多半是镜像没正确构建或 tar 解压失败。
set -euo pipefail

: "${GH_OWNER:?GH_OWNER required}"
: "${GH_REPO:?GH_REPO required}"
: "${GH_RUNNER_TOKEN:?GH_RUNNER_TOKEN required}"

RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,k8s-deployer}"
RUNNER_NAME="${RUNNER_NAME:-k8s-deployer-$(hostname)}"
RUNNER_DIR="${RUNNER_DIR:-/home/deployer/actions-runner}"

# Preflight：actions-runner tarball 是否解压到位
for f in config.sh run.sh; do
  if [ ! -x "${RUNNER_DIR}/${f}" ]; then
    if [ -f "${RUNNER_DIR}/${f}" ]; then
      chmod +x "${RUNNER_DIR}/${f}"
    else
      echo "::error::Missing ${RUNNER_DIR}/${f} — actions-runner tarball not extracted properly. Check Dockerfile." >&2
      exit 1
    fi
  fi
done

# Preflight：kubectl 能连上集群？（kubeconfig 必须由 deployment.yaml 的 secret volume 挂进来）
if ! kubectl version --client >/dev/null 2>&1; then
  echo "::error::kubectl not installed; check Dockerfile" >&2
  exit 1
fi
if [ -n "${KUBECONFIG:-}" ] && [ ! -r "${KUBECONFIG}" ]; then
  echo "::warning::KUBECONFIG=${KUBECONFIG} not readable; deploy.py will fail until secret is mounted"
fi

cd "${RUNNER_DIR}"

./config.sh --unattended \
  --url "https://github.com/${GH_OWNER}/${GH_REPO}" \
  --token "${GH_RUNNER_TOKEN}" \
  --name "${RUNNER_NAME}" \
  --labels "${RUNNER_LABELS}" \
  --work _work \
  --replace

trap 'echo "[entrypoint] removing runner"; ./config.sh remove --token "${GH_RUNNER_TOKEN}" || true' EXIT

exec ./run.sh
