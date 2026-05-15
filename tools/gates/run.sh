#!/usr/bin/env bash
# 4 项确定性门禁主入口。退出码 0 = 全过；非 0 = 详见 gates.md 表。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

failures=()

gates_run_check sensitive-info    || failures+=("sensitive-info:$?")
gates_run_check design-doc        || failures+=("design-doc:$?")
gates_run_check vulnerability     || failures+=("vulnerability:$?")
gates_run_check license-compliance || failures+=("license:$?")

if [ ${#failures[@]} -eq 0 ]; then
  log "all gates passed"
  exit 0
fi

log "gates failed: ${failures[*]}"
# Attempt automatic fixes for the recoverable ones
bash "${SCRIPT_DIR}/fixes.sh" "${failures[@]}" || true

# Re-check after fix attempts
failures2=()
for f in "${failures[@]}"; do
  name="${f%%:*}"
  gates_run_check "${name}" || failures2+=("${name}:$?")
done

if [ ${#failures2[@]} -eq 0 ]; then
  log "all gates passed after auto-fix"
  exit 0
fi

log "gates still failing after auto-fix: ${failures2[*]}"
case "${failures2[0]%%:*}" in
  sensitive-info)     exit 10 ;;
  design-doc)         exit 20 ;;
  vulnerability)      exit 30 ;;
  license-compliance) exit 40 ;;
  *)                  exit 99 ;;
esac
