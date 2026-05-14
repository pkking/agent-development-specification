#!/usr/bin/env bash
# 多 agent 对抗编排主调度。
# 加载团队 + 项目层 prompt，串联 design / dev / review / tester 4 agent + 4 项确定性门禁。
# 文档：../../docs/pipeline/generic-layer/orchestrator.md
set -euo pipefail

: "${PROJECT:?PROJECT required}"
: "${ISSUE_NUMBER:?}"
: "${REQUIREMENT_PR:?}"
: "${GITHUB_WORKSPACE:?}"
: "${GH_TOKEN:?}"

MAX_FIX_ROUNDS="${MAX_FIX_ROUNDS:-3}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATES_RUN="${SCRIPT_DIR}/../gates/run.sh"
TESTS_RUN="${SCRIPT_DIR}/../tests/run_layered.sh"

log() { printf '[orchestrate %s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

run_agent() {
  local agent_name="$1"
  log "running agent: ${agent_name}"
  # Each agent is invoked via Claude CLI with the team + project prompts.
  # The actual prompt assembly is project-specific; this orchestrator only sequences the calls.
  claude -p --bare \
    --mcp-config "${MCP_CONFIG:-/etc/mcp/config.json}" \
    --permission-mode bypassPermissions \
    --output-format text \
    < "${SCRIPT_DIR}/prompts/${agent_name}.md"
}

# ---- main loop ----
log "start orchestrate for issue #${ISSUE_NUMBER} project=${PROJECT}"

# 1. design agent
run_agent design

# 2. dev agent + gates loop
round=0
while :; do
  run_agent dev

  if "${GATES_RUN}"; then
    log "gates passed at round=${round}"
    break
  fi

  round=$((round + 1))
  if [ "${round}" -ge "${MAX_FIX_ROUNDS}" ]; then
    log "MAX_FIX_ROUNDS exceeded; marking needs-human"
    gh issue comment "${ISSUE_NUMBER}" --body "❌ gates failed after ${MAX_FIX_ROUNDS} rounds; needs human"
    exit 1
  fi
  log "gates failed; entering fix round ${round}"
done

# 3. review agent (1 pass + dev fix)
run_agent review
run_agent dev   # apply review feedback

# 4. tester agent
run_agent tester
"${TESTS_RUN}" smoke
"${TESTS_RUN}" unit
"${TESTS_RUN}" contract

# 5. trigger deployer (decoupled via repository_dispatch — caller workflow handles this)
log "orchestrate complete; signaling caller to dispatch deploy"
