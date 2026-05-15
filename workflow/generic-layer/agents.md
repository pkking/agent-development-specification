# Generic Layer — 5 Agents

> 5 个 AI agent 串成对抗循环（requirements-doc → design → dev → deploy → review + tester），由 [`orchestrator.md`](orchestrator.md) 调度。
> 注：deploy 是脚本不是 agent，但放在 dev 与 review/tester 之间承担「起预览」职责。

## 1. 总览

| Agent | 职责 | 团队级 baseline prompt | 项目级 prompt（om-datacenter 实例） | 输出 |
|---|---|---|---|---|
| **requirements-doc**（Workflow A） | 把 issue 转需求分析说明书 | [`../../teams/prompts/requirements-doc.md`](../../teams/prompts/requirements-doc.md) | [`../../projects/om-datacenter/.github/agents/requirements-doc.md`](../../projects/om-datacenter/.github/agents/requirements-doc.md) | backlog 仓 PR + issue 回评 |
| **design**（Workflow B 第 1 棒） | 出技术设计 + 验收标准 + 路由 | [`../../teams/prompts/design.md`](../../teams/prompts/design.md) | [`../../projects/om-datacenter/.github/agents/design.md`](../../projects/om-datacenter/.github/agents/design.md) | `route.json` + `design.md` |
| **dev**（第 2 棒） | 实现代码 + UT + 开 PR | [`../../teams/prompts/dev.md`](../../teams/prompts/dev.md) | [`../../projects/om-datacenter/.github/agents/dev.md`](../../projects/om-datacenter/.github/agents/dev.md) | 各 dev 仓 PR + `result.json` |
| **review**（第 3 棒） | 跑门禁 + 对抗式 review diff | [`../../teams/prompts/review.md`](../../teams/prompts/review.md) | [`../../projects/om-datacenter/.github/agents/review.md`](../../projects/om-datacenter/.github/agents/review.md) | `review_report.md` + 打回清单 |
| **tester**（第 4 棒） | 4 类测试 + 报告 | [`../../teams/prompts/tester.md`](../../teams/prompts/tester.md) | [`../../projects/om-datacenter/.github/agents/tester.md`](../../projects/om-datacenter/.github/agents/tester.md) | `test_report.md` + 打回清单 + 复盘 |

PR 评论格式 / release notes 等**非 agent 角色**的公共 prompt：[`../../teams/prompts/pr-comment.md`](../../teams/prompts/pr-comment.md) / [`../../teams/prompts/release-notes.md`](../../teams/prompts/release-notes.md)。

## 2. 对抗机制

- design / dev 是「生产者」
- review / tester 是「挑战者」，反馈错就回 dev（或 design，若指出设计层问题）
- 最多 `MAX_FIX_ROUNDS` 轮（默认 3），超出标 `needs-human`

## 3. 项目层覆盖

每个项目在 `../../projects/<project>/.github/agents/<agent>.md` 加项目专属 prompt **追加加载**在团队 baseline 之后。覆盖原则见下方 §4 加载顺序。

## 4. 加载顺序

```
个人层 ~/.claude/CLAUDE.md                       优先级最高
    ↓
项目层 projects/<project>/CLAUDE.md
    ↓
团队层 teams/CLAUDE.md
    ↓
团队级 agent baseline prompt（teams/prompts/<agent>.md）
    ↓
项目级 agent prompt（projects/<project>/.github/agents/<agent>.md）
```

后加载的可覆盖先加载的同名小节。

## 5. 关联

- 编排：[`orchestrator.md`](orchestrator.md)
- 真实 agent prompt 实例：[`../../projects/om-datacenter/.github/agents/`](../../projects/om-datacenter/.github/agents/)
- 团队 prompt 总入口：[`../../teams/prompts/`](../../teams/prompts/)
