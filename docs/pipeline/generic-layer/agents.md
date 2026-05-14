# Generic Layer — 4 Agents

> 4 个 AI agent 互相对抗，由 [`orchestrator.md`](orchestrator.md) 调度。

## 1. 总览

| Agent | 职责 | 加载的团队 prompt | 输出 |
|---|---|---|---|
| design | 把需求转架构设计 | [`../../teams/prompts/architecture-design.md`](../../teams/prompts/architecture-design.md) | `docs/architecture.md` 更新 |
| dev | 实现代码 + UT | [`../../teams/prompts/development.md`](../../teams/prompts/development.md) | 代码 + UT + release notes 片段 |
| review | 评审 design + dev 产物 | [`../../teams/prompts/pr-comment.md`](../../teams/prompts/pr-comment.md) + 团队规范 | 评审评论 + 失败原因 |
| tester | 跑分层测试 + 出报告 | [`../../teams/prompts/test-strategy.md`](../../teams/prompts/test-strategy.md) | 测试用例 + 报告 |

## 2. 对抗机制

- design / dev 是「生产者」
- review / tester 是「挑战者」，反馈错就回 dev / design 修
- 最多 `MAX_FIX_ROUNDS` 轮（默认 3），超出标 `needs-human`

## 3. 项目层覆盖

每个项目可以在 `../../projects/<project>/prompts/` 加项目专属 prompt 覆盖团队 prompt 的部分章节（例如换文档模板路径、加项目铁规）。

## 4. 加载顺序

```
个人层 ~/.claude/CLAUDE.md
    ↓
项目层 projects/<project>/CLAUDE.md
    ↓
团队层 teams/CLAUDE.md
    ↓
对应 agent 的团队 prompt（这一文档表格中的链接）
    ↓
项目层 agent prompt（如有）
```

后加载的可覆盖先加载的同名小节。

## 5. 关联

- 编排：[`orchestrator.md`](orchestrator.md)
- 公共 agent 实现：参考 `../../projects/om-datacenter/` 的实际 issue-2 实现（已 inline 在 orchestrate.sh 中）
- 团队 prompt 总入口：[`../../teams/prompts/`](../../teams/prompts/)
