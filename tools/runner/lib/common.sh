#!/usr/bin/env bash
# Shared functions for self-hosted GitHub Actions runner scripts.
# Source this file: source "$(dirname "$0")/../lib/common.sh"
set -euo pipefail

# ── require_env ──────────────────────────────────────────────────────────────────
# Validate that required environment variables are set. Exits with error if any are
# missing. Usage: require_env GH_OWNER GH_REPO GH_RUNNER_TOKEN
require_env() {
  local missing=()
  for var in "$@"; do
    if [ -z "${!var:-}" ]; then
      missing+=("$var")
    fi
  done
  if [ ${#missing[@]} -gt 0 ]; then
    echo "::error::Missing required env vars: ${missing[*]}" >&2
    exit 1
  fi
}

# ── build_and_push ───────────────────────────────────────────────────────────────
# Build and push a multi-arch Docker image. Falls back to legacy docker build+push
# when buildx is not available.
#
# Usage: build_and_push <registry> <image_name> [tag] [platforms]
#   registry   — e.g. registry.example.com/team
#   image_name — e.g. ai-dev-runner
#   tag        — defaults to YYYYMMDD-HHMMSS
#   platforms  — defaults to linux/amd64,linux/arm64
build_and_push() {
  local registry="${1:?registry required}"
  local image_name="${2:?image_name required}"
  local tag="${3:-$(date +%Y%m%d-%H%M%S)}"
  local platforms="${4:-linux/amd64,linux/arm64}"

  local full="${registry}/${image_name}"

  if docker buildx version >/dev/null 2>&1; then
    docker buildx build --platform "${platforms}" \
      -t "${full}:${tag}" -t "${full}:latest" \
      --push .
  else
    docker build -t "${full}:${tag}" -t "${full}:latest" .
    docker push "${full}:${tag}"
    docker push "${full}:latest"
  fi

  echo "[build-and-push] pushed ${full}:${tag} and ${full}:latest"
}

# ── runner_preflight ─────────────────────────────────────────────────────────────
# Verify that actions-runner tarball has been extracted properly.
# Usage: runner_preflight <runner_dir>
runner_preflight() {
  local runner_dir="${1:?runner_dir required}"

  for f in config.sh run.sh; do
    if [ ! -x "${runner_dir}/${f}" ]; then
      if [ -f "${runner_dir}/${f}" ]; then
        chmod +x "${runner_dir}/${f}"
      else
        echo "::error::Missing ${runner_dir}/${f} — actions-runner tarball not extracted. Check Dockerfile." >&2
        exit 1
      fi
    fi
  done
}

# ── register_runner ──────────────────────────────────────────────────────────────
# Register a self-hosted runner and set up EXIT trap for cleanup.
#
# Registration tokens are one-time use — consumed by config.sh. The trap attempts
# removal with GH_PAT (if set), falling back to the registration token (which will
# likely fail since it's already consumed). The || true ensures the container still
# exits cleanly; GitHub auto-removes offline runners after a grace period.
#
# Usage: register_runner <runner_dir> <gh_owner> <gh_repo> <gh_token> <name> <labels>
register_runner() {
  local runner_dir="${1:?}"
  local gh_owner="${2:?}"
  local gh_repo="${3:?}"
  local gh_token="${4:?}"
  local runner_name="${5:?}"
  local runner_labels="${6:?}"

  cd "${runner_dir}"

  ./config.sh --unattended \
    --url "https://github.com/${gh_owner}/${gh_repo}" \
    --token "${gh_token}" \
    --name "${runner_name}" \
    --labels "${runner_labels}" \
    --work _work \
    --replace

  if [ -n "${GH_PAT:-}" ]; then
    trap 'echo "[entrypoint] removing runner (using GH_PAT)"; ./config.sh remove --pat "${GH_PAT}" || true' EXIT
  else
    trap 'echo "[entrypoint] removing runner (token may be consumed; set GH_PAT for reliable cleanup)"; ./config.sh remove --token "${gh_token}" 2>/dev/null || true' EXIT
  fi
}
