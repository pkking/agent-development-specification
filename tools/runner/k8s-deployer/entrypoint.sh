#!/usr/bin/env bash
# k8s-deployer container entrypoint — register self-hosted runner, then listen for jobs.
#
# Dependencies:
#   config.sh / run.sh — from actions/runner tarball, extracted by Dockerfile to
#   /home/deployer/actions-runner/. If missing, the preflight check will fail with a
#   clear error.
#
#   kubectl + KUBECONFIG — needed for deploy.py. KUBECONFIG is mounted by
#   deployment.yaml via a Secret volume. This script checks that kubectl is installed
#   and warns if KUBECONFIG is not readable yet.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

require_env GH_OWNER GH_REPO GH_RUNNER_TOKEN

RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,k8s-deployer}"
RUNNER_NAME="${RUNNER_NAME:-k8s-deployer-$(hostname)}"
RUNNER_DIR="${RUNNER_DIR:-/home/deployer/actions-runner}"

runner_preflight "${RUNNER_DIR}"

# Preflight: kubectl available?
if ! kubectl version --client >/dev/null 2>&1; then
  echo "::error::kubectl not installed; check Dockerfile" >&2
  exit 1
fi
if [ -n "${KUBECONFIG:-}" ] && [ ! -r "${KUBECONFIG}" ]; then
  echo "::warning::KUBECONFIG=${KUBECONFIG} not readable; deploy.py will fail until Secret is mounted"
fi

register_runner "${RUNNER_DIR}" "${GH_OWNER}" "${GH_REPO}" "${GH_RUNNER_TOKEN}" "${RUNNER_NAME}" "${RUNNER_LABELS}"

exec ./run.sh
