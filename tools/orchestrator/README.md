# orchestrator/orchestrate.sh

> Workflow B 主逻辑: 4 个 AI agent (design / dev / review / tester) 多轮对抗.

## 输入(环境变量)

- `SOURCE_REPO`
- `ISSUE_NUMBER`
- `BRANCH`
- `GH_TOKEN`
- `GITHUB_WORKSPACE`
- `MAX_FIX_ROUNDS` (默认 3)

## 输出

- 各 dev 仓的 head=`<BRANCH>` open PR
- `/tmp/opencode/*` 各 agent 产物

## 关联

- [`../../pipeline/generic-layer/orchestrator.md`](../../pipeline/generic-layer/orchestrator.md)
- [`../../pipeline/generic-layer/agents.md`](../../pipeline/generic-layer/agents.md)
