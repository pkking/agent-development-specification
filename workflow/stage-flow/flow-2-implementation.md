# 流程 2 — 4 Agent 对抗实现 + 起预览

> 评论 `[<服务名>需求实现]` 触发。4 个 AI agent 互相对抗，产出可上预览的 PR。

## 1. 触发

| 项       | 值                                                                     |
| -------- | ---------------------------------------------------------------------- |
| 入口评论 | `[<服务名>需求实现]`                                                   |
| 前置     | 流程 1 的需求 PR 必须已合入                                            |
| 跑在哪   | ai-dev-runner + k8s-deployer                                           |
| 主调度   | [`../generic-layer/orchestrator.md`](../generic-layer/orchestrator.md) |

## 2. 4 个 agent

详见 [`../generic-layer/agents.md`](../generic-layer/agents.md)：design → dev → review → tester。

## 3. 步骤

```
1. 拉取已合入的需求文档
2. design agent 出架构设计 + 提 PR 到 dev 仓
3. dev agent 实现 + UT
4. 跑 4 项确定性门禁（gates.md），不过则修，最多 MAX_FIX_ROUNDS 轮
5. review agent 评审，提反馈则 dev 再迭代
6. tester agent 跑分层测试（tests.md）
7. 调 k8s-deployer 起预览（deployer.md）
8. 评论 PR：预览 URL + 测试报告 + 覆盖率
```

## 4. 输出

- dev 仓 PR（含代码 + UT + 文档 + release notes 片段）
- 预览 URL（独立 ingress 域名）
- 测试报告（JUnit XML + 覆盖率）

## 5. 失败处理

- gates 不过且自动修无效 → 标 `needs-human`
- 部署 readiness 超时 → 标 `deploy-failed`
- 单 agent 连续报错 → 标 `agent-error`

## 6. 下一步

- 评审通过后，maintainer 评 `[<服务名>需求上线]` → 进入流程 3

## 7. 关联

- 编排：[`../generic-layer/orchestrator.md`](../generic-layer/orchestrator.md)
- 4 agent：[`../generic-layer/agents.md`](../generic-layer/agents.md)
- 部署：[`../generic-layer/deployer.md`](../generic-layer/deployer.md)
- 测试：[`../generic-layer/tests.md`](../generic-layer/tests.md)
- 门禁：[`../generic-layer/gates.md`](../generic-layer/gates.md)
- 评论协议：[`../pr-comment-protocol.md`](../pr-comment-protocol.md)
