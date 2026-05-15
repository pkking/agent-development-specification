#!/usr/bin/env bash
# Build + push k8s-deployer image.
# Usage: REGISTRY=<your-registry>/<team> ./build-and-push.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

REGISTRY="${REGISTRY:?REGISTRY required, e.g. registry.example.com/team}"
build_and_push "${REGISTRY}" "${IMAGE_NAME:-k8s-deployer}" "${TAG:-$(date +%Y%m%d-%H%M%S)}" "${PLATFORMS:-linux/amd64,linux/arm64}"
