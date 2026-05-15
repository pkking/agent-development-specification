# 阶段 1 — Issue 提交

> 在 backlog 仓提一条 issue，作为整条流水线的入口。

## 1. 谁触发

业务方 / 内部 PM / 一线运维 / 任何团队成员。

## 2. 做什么

| 步骤 | 操作                                                     |
| ---- | -------------------------------------------------------- |
| 1    | 进入 `opensourceways/backlog` 仓的 Issues 页面           |
| 2    | 点 New Issue，选合适模板（Feature Request / Bug Report） |
| 3    | 标题：`[<服务名>] <一句话场景描述>`                      |
| 4    | 正文：背景 + 现状 + 期望；按 issue 模板填字段            |
| 5    | 不打 `accepted` 标签（由 maintainer 在阶段 2 打）        |

## 3. 团队 issue 工作流

详尽规则与字段示例：[`../../teams/context/team/issue-workflow-guide.md`](../../teams/context/team/issue-workflow-guide.md)。

## 4. 不允许

- 在 issue 正文贴真实凭据（即便是测试环境的）
- 直接在 dev 仓提需求 issue（dev 仓只放 PR）

## 5. 下一步

- maintainer 在 issue 上评 `/accepts` → 进入阶段 2

## 6. 关联

- 阶段 2：[`stage-2-acceptance.md`](stage-2-acceptance.md)
- 全景：[`../architecture.md`](../architecture.md)
