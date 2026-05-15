# Common helpers for gates/. Sourced by run.sh / checks.sh / fixes.sh.

log() { printf '[gates %s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

gates_run_check() {
  local name="$1"
  local fn
  case "${name}" in
    sensitive-info)     fn=check_sensitive_info ;;
    design-doc)         fn=check_design_doc ;;
    vulnerability)      fn=check_vulnerability ;;
    license-compliance) fn=check_license_compliance ;;
    *)                  log "unknown gate: ${name}"; return 99 ;;
  esac
  # shellcheck disable=SC1091
  source "$(dirname "${BASH_SOURCE[0]}")/checks.sh"
  "${fn}"
}
