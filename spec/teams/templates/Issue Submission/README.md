# Issue 提交模板（Stage 1 用）

> 业务方在 backlog 仓提需求 issue 时选用的 GitHub 表单模板。
> 实际部署位置：backlog 仓的 `.github/ISSUE_TEMPLATE/`。本目录是**代表副本**，供 spec 仓内部引用。

## 两种基本模板

| 文件                                         | 用途                      |
| -------------------------------------------- | ------------------------- |
| [`Feature Request.md`](Feature%20Request.md) | 新增功能 / 体验改进类需求 |
| [`Bug Report.md`](Bug%20Report.md)           | 缺陷 / 异常修复类需求     |

## 选哪个

- 标题含 `[需求]` → Feature Request（流程 1 走 ra-doc 模式写需求分析说明书 PR）
- 标题含 `[缺陷]` / `[任务]` / 不含上述关键字 → Bug Report 或自由格式（流程 1 走 user-view 模式只回评，不写文档）

判定逻辑详见 [`../../../projects/om-datacenter/.github/workflows/issue-1-analyze-requirement.yml`](../../../projects/om-datacenter/.github/workflows/issue-1-analyze-requirement.yml) 的 `Decide A_MODE` 步骤。

## 关联

- 全流程：[`../../../pipeline/architecture.md`](../../../pipeline/architecture.md) §阶段 1
- 团队 issue 工作流总览：[`../../context/team/issue-workflow-guide.md`](../../context/team/issue-workflow-guide.md)
- 需求文档（流程 1 产出）模板：[`../Requirement Analysis/`](../Requirement%20Analysis/)
