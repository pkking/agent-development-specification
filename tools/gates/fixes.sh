#!/usr/bin/env bash
# Auto-fixes for recoverable gate failures. Called by run.sh with failure list.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

for failure in "$@"; do
  name="${failure%%:*}"
  case "${name}" in
    sensitive-info)
      log "fix sensitive-info: not auto-fixable; require human intervention"
      ;;
    design-doc)
      log "fix design-doc: dev agent should be re-invoked with prompt to update docs/"
      ;;
    vulnerability)
      log "fix vulnerability: not auto-fixable"
      ;;
    license-compliance)
      log "fix license-compliance: adding SPDX header to new source files"
      # Best-effort header injection for new files
      while IFS= read -r f; do
        case "${f}" in
          *.py|*.js|*.ts|*.go|*.sh)
            if ! head -n 5 "${f}" | grep -q 'SPDX-License-Identifier'; then
              tmp="$(mktemp)"
              printf '# SPDX-License-Identifier: Apache-2.0\n%s\n' "$(cat "${f}")" > "${tmp}"
              mv "${tmp}" "${f}"
            fi
            ;;
        esac
      done < <(git diff --name-only --diff-filter=A "${GITHUB_BASE_REF:-origin/main}"...HEAD)
      ;;
    *)
      log "fix: no auto-fix recipe for ${name}"
      ;;
  esac
done
