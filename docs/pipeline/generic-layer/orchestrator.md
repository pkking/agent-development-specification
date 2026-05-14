# Generic Layer — Orchestrator

> 单 PR 内多 agent 协作的总编排。代码：[`../../src/orchestrator/`](../../src/orchestrator/)。

## 1. 角色

`orchestrate.sh` 是 4 agent 对抗循环的总调度，串联 design / dev / review / tester 4 个 agent 与 4 项确定性门禁。

## 2. 输入

- `ISSUE_NUMBER` — backlog 仓 issue 号
- `REQUIREMENT_PR` — 已合入的需求 PR 号
- `PROJECT` — 项目名
- `MAX_FIX_ROUNDS` — 自动修复轮数上限（默认 3）

## 3. 主循环

```
1. design agent → 产出 architecture-design.md
2. dev agent    → 实现 + UT
3. 跑 4 项确定性门禁（gates.md）
   ├─ 任一不通过 → 进入修复轮（最多 MAX_FIX_ROUNDS）
   └─ 全过 → 进下一步
4. review agent → 评审代码 + 文档
   └─ 提反馈 → dev agent 修复（不计入 fix round）
5. tester agent → 跑 tests.md 描述的分层测试
   └─ 失败 → dev agent 修复（不计入 fix round）
6. 全过 → 触发部署器起预览（deployer.md）
7. 回写 PR 评论：预览 URL + 测试报告 + 覆盖率
```

## 4. 错误退出

- `MAX_FIX_ROUNDS` 用完仍未过门禁 → 评论 PR 标记 `needs-human`，退出码 1
- 任一 agent 报错 > 3 次连续 → 评论 PR 标记 `agent-error`，退出码 2
- 部署器返回 readiness 超时 → 评论 PR 标记 `deploy-failed`，退出码 3

## 5. 跨 PR 状态

- 当前 round 数 / 反馈历史存在 PR 评论的特定 marker 中（机器可读），见 [`../pr-comment-protocol.md`](../pr-comment-protocol.md)
- 不依赖外部 DB，PR 关闭即天然清理

## 6. 关联

- 4 agent prompt：[`agents.md`](agents.md)
- 确定性门禁：[`gates.md`](gates.md)
- 测试编排：[`tests.md`](tests.md)
- 部署：[`deployer.md`](deployer.md)
- 编排代码：[`../../src/orchestrator/`](../../src/orchestrator/)
