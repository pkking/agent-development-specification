#!/usr/bin/env bash
# 多 agent 对抗编排主调度。
# 加载：团队 baseline prompt（teams/prompts/<agent>.md）+ 项目层 agent prompt（projects/<project>/.github/agents/<agent>.md），
# 串联 design → dev → deploy → review + tester，最多 MAX_FIX_ROUNDS 轮对抗。
# 文档：../../pipeline/generic-layer/orchestrator.md
set -euo pipefail

: "${PROJECT:?PROJECT required}"
: "${ISSUE_NUMBER:?}"
: "${SOURCE_REPO:?}"
: "${BRANCH:?}"
: "${GITHUB_WORKSPACE:?}"
: "${WORKSPACE_DIR:?WORKSPACE_DIR required (per-issue PVC workdir)}"
: "${GH_TOKEN:?}"

MAX_FIX_ROUNDS="${MAX_FIX_ROUNDS:-3}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_ROOT="${SPEC_ROOT:-${GITHUB_WORKSPACE}}"                 # umbrella checkout root
TEAMS_PROMPTS="${SPEC_ROOT}/docs/teams/prompts"
PROJECT_AGENTS="${SPEC_ROOT}/docs/projects/${PROJECT}/.github/agents"

GATES_RUN="${SCRIPT_DIR}/../gates/run.sh"
TESTS_RUN="${SCRIPT_DIR}/../tests/run_layered.sh"
DEPLOYER="${SCRIPT_DIR}/../deployer/deploy.py"

log() { printf '[orchestrate %s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

# Build prompt = team baseline + project override (in that order)
build_prompt() {
  local agent="$1"
  local team_p="${TEAMS_PROMPTS}/${agent}.md"
  local proj_p="${PROJECT_AGENTS}/${agent}.md"
  [ -f "$team_p" ] || { log "missing team prompt: $team_p"; return 2; }
  cat "$team_p"
  if [ -f "$proj_p" ]; then
    printf '\n\n---\n\n# Project-level addendum (%s)\n\n' "${PROJECT}"
    cat "$proj_p"
  fi
}

run_agent() {
  local agent="$1"
  log "running agent: ${agent}"
  local prompt_file
  prompt_file="$(mktemp)"
  build_prompt "$agent" > "$prompt_file"
  # Invoke whichever LLM CLI is installed on the runner. om-datacenter currently uses opencode;
  # spec-recommended baseline uses claude-code. Pick by feature detection.
  if command -v opencode >/dev/null 2>&1; then
    opencode run "$(cat "$prompt_file")" \
      --model "${OPENCODE_MODEL:-alibaba-cn/glm-5}" \
      --agent build \
      --dangerously-skip-permissions --thinking=false
  else
    claude -p --bare \
      --mcp-config "${MCP_CONFIG:-/etc/mcp/config.json}" \
      --permission-mode bypassPermissions \
      --output-format text < "$prompt_file"
  fi
  rm -f "$prompt_file"
}

# ---- main loop ----
log "start orchestrate for issue #${ISSUE_NUMBER} project=${PROJECT} branch=${BRANCH}"

# 1. design agent → /tmp/opencode/route.json + /tmp/opencode/design.md
run_agent design

# 2. dev → gates loop
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
    gh issue comment "${ISSUE_NUMBER}" --repo "${SOURCE_REPO}" \
      --body "❌ gates failed after ${MAX_FIX_ROUNDS} rounds; needs human"
    exit 1
  fi
  log "gates failed; entering fix round ${round}"
done

# 3. deploy 每个 PR → /tmp/opencode/deploy/pr-<N>.json
mkdir -p /tmp/opencode/deploy
python3 -c "import json,sys; d=json.load(open('/tmp/opencode/result.json')); [print(p['number']) for p in d.get('prs',[])]" \
  | while read -r pr_number; do
      [ -z "$pr_number" ] && continue
      log "deploying preview for PR #${pr_number}"
      python3 "${DEPLOYER}" \
        --project "${PROJECT}" \
        --service "${PROJECT}" \
        --mode "${DEPLOY_MODE:-dev-pod}" \
        --image "<set by per-project hook>" \
        --pr-number "${pr_number}" \
        --namespace "${NAMESPACE:-ai-test}" \
        --base-domain "${BASE_DOMAIN:-ai.test.osinfra.cn}" \
        > "/tmp/opencode/deploy/pr-${pr_number}.json"
    done

# 4. review + tester (两个挑战者，按 review→tester 顺序跑；feedback 合并由 caller workflow 处理)
run_agent review
run_agent tester
"${TESTS_RUN}" smoke
"${TESTS_RUN}" unit
"${TESTS_RUN}" contract

# 5. 有打回内容 → 回 dev/design 重跑（这里简化：交由外层 workflow 决定）
if [ -s /tmp/opencode/review_fail.md ] || [ -s /tmp/opencode/test_fail.md ]; then
  log "review/tester returned defects; orchestrator delegates next iteration to caller workflow"
fi

log "orchestrate complete"
