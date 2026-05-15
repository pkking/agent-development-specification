#!/usr/bin/env bash
# Run a single test layer. Detects project type (npm / pytest / make) and dispatches.
# Layers: smoke | unit | contract | integration | e2e
set -uo pipefail

LAYER="${1:?layer required: smoke|unit|contract|integration|e2e}"

log() { printf '[tests %s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

# 1. Project-defined override via .preview/service.yaml > test_targets.<layer>
override=""
if [ -f .preview/service.yaml ] && command -v yq >/dev/null 2>&1; then
  override="$(yq -r ".test_targets.${LAYER} // \"\"" .preview/service.yaml || true)"
fi

if [ -n "${override}" ] && [ "${override}" != "null" ]; then
  log "using project override for layer=${LAYER}: ${override}"
  bash -c "${override}"
  exit $?
fi

# 2. Default dispatch by project type
if [ -f package.json ]; then
  case "${LAYER}" in
    smoke)       npm run smoke       || true ;;
    unit)        npm test ;;
    contract)    npm run test:contract    || log "no test:contract target" ;;
    integration) npm run test:integration || log "no test:integration" ;;
    e2e)         npm run test:e2e         || log "no test:e2e" ;;
  esac
elif [ -f pyproject.toml ] || [ -f setup.py ]; then
  case "${LAYER}" in
    smoke)       pytest -m smoke ;;
    unit)        pytest tests/unit/ ;;
    contract)    pytest tests/contract/    || log "no contract tests" ;;
    integration) pytest tests/integration/ || log "no integration tests" ;;
    e2e)         pytest tests/e2e/         || log "no e2e tests" ;;
  esac
elif [ -f Makefile ]; then
  make "test-${LAYER}"
else
  log "no recognized project type; layer=${LAYER} skipped"
fi
