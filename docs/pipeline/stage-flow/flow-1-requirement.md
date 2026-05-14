# 流程 1 — 需求分析

> 评论 `[<服务名>需求分析]` 触发。AI 自动写需求文档 PR。

## 1. 触发

| 项 | 值 |
|---|---|
| 入口评论 | `[<服务名>需求分析]` |
| 跑在哪 | ai-dev-runner |
| 加载 prompt | [`../../teams/prompts/requirement-analysis.md`](../../teams/prompts/requirement-analysis.md) + 项目层覆盖（如有） |
| 工具 | Claude CLI + gh |

## 2. 步骤

1. 拉取 issue 全文（包括评论）
2. 拉取当前服务现状（`docs/architecture.md` 等）
3. design agent 起草需求文档：背景 → 范围 → 用户场景 → 功能清单 → 非功能 → 接口 → 依赖与风险 → 验收 → 不做什么
4. 在 backlog 仓开 PR，文件名 `<issue-id>-<short-slug>-requirement.md`
5. 评论 issue：「需求 PR 已出 → `<pr-url>`」

## 3. 必产出

按 [`../../teams/templates/Requirement Analysis/`](../../teams/templates/Requirement%20Analysis/) 模板。

## 4. 评审

- 需求 PR 由项目 owner + 业务方共同评审
- 评审通过 + 合入后才能进流程 2

## 5. 失败处理

- AI 起草不符合模板 → 在 PR 上评 review，AI 再迭代（一轮）
- 仍不符 → 标 `needs-human`，maintainer 接手

## 6. 下一步

- 流程 1 PR 合入后，评 `[<服务名>需求实现]` → 进入流程 2

## 7. 关联

- 团队 prompt：[`../../teams/prompts/requirement-analysis.md`](../../teams/prompts/requirement-analysis.md)
- 全景：[`../architecture.md`](../architecture.md)
- 流程 2：[`flow-2-implementation.md`](flow-2-implementation.md)
