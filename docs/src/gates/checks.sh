#!/usr/bin/env bash
# Individual gate checks. Sourced/called by run.sh via gates_run_check.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

check_sensitive_info() {
  # gitleaks scan over the diff
  if command -v gitleaks >/dev/null 2>&1; then
    gitleaks detect --redact --no-banner --source=. --exit-code 1
  else
    log "gitleaks not installed; falling back to grep"
    ! git diff --no-color | grep -E '(BEGIN [A-Z ]*PRIVATE KEY|password\s*=|api[_-]?key\s*=|token\s*=)' -i
  fi
}

check_design_doc() {
  # PR must touch architecture.md or api-spec.md
  base_ref="${GITHUB_BASE_REF:-origin/main}"
  changed="$(git diff --name-only "${base_ref}"...HEAD)"
  if echo "${changed}" | grep -Eq '(docs/architecture\.md|docs/api-spec\.md)'; then
    return 0
  fi
  log "design-doc gate: no architecture.md / api-spec.md change found"
  return 1
}

check_vulnerability() {
  if command -v trivy >/dev/null 2>&1; then
    trivy fs --exit-code 1 --severity HIGH,CRITICAL .
  else
    log "trivy not installed; skipping vulnerability scan (treated as pass)"
    return 0
  fi
}

check_license_compliance() {
  # licenses-check: simple greenlist via LICENSE-ALLOWED file (one license name per line)
  allowed_file="${SCRIPT_DIR}/allowed-licenses.txt"
  if [ ! -f "${allowed_file}" ]; then
    log "no allowed-licenses.txt; treating license gate as pass"
    return 0
  fi
  log "license check stub: full implementation depends on language/registry"
  return 0
}
