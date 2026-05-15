#!/usr/bin/env bash
# ai-dev-runner container entrypoint — register self-hosted runner, then listen for jobs.
#
# Dependencies:
#   config.sh / run.sh — from actions/runner tarball, extracted by Dockerfile to
#   /home/runner/actions-runner/. If missing, the preflight check will fail with a
#   clear error.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

require_env GH_OWNER GH_REPO GH_RUNNER_TOKEN

RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,ai-dev-runner}"
RUNNER_NAME="${RUNNER_NAME:-ai-dev-$(hostname)}"
RUNNER_DIR="${RUNNER_DIR:-/home/runner/actions-runner}"

runner_preflight "${RUNNER_DIR}"
register_runner "${RUNNER_DIR}" "${GH_OWNER}" "${GH_REPO}" "${GH_RUNNER_TOKEN}" "${RUNNER_NAME}" "${RUNNER_LABELS}"

exec ./run.sh
