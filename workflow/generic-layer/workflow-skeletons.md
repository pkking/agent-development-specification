# Generic Layer — Workflow 骨架

> 通用流水线提供的 3 个 GitHub Actions workflow 骨架；项目仓的 caller workflow 通过 `workflow_call` 引用。

## 1. 3 个骨架

| 骨架                                | 触发                                         | 项目 caller 文件名                       |
| ----------------------------------- | -------------------------------------------- | ---------------------------------------- |
| `issue-1-analyze-requirement.yml`   | issue_comment `[<服务名>需求分析]`           | `caller-workflow.yml` 中 dispatch 此 job |
| `issue-2-implement-and-preview.yml` | issue_comment `[<服务名>需求实现]`           | 同上                                     |
| `issue-3-merge-and-deploy.yml`      | issue_comment `[<服务名>需求上线]`（白名单） | 同上                                     |

## 2. 骨架职责

### 2.1 issue-1-analyze-requirement

- 解析 issue 内容
- 调 design agent → 起草需求文档
- 提 PR 到 backlog 仓
- 评论 PR 链接到原 issue

### 2.2 issue-2-implement-and-preview

- 等需求 PR 合入
- 调 orchestrator.sh → 4 agent 对抗
- 触发 deployer → 起预览
- 评论预览 URL + 测试报告 + 覆盖率

### 2.3 issue-3-merge-and-deploy

- 校验评论人在 maintainer 白名单
- 合所有相关 PR（dev 仓 + backlog 仓）
- 触发部署到 beta namespace
- 清理预览资源

## 3. 项目接线

项目 caller workflow 模板见 [`../project-layer/caller-workflow-spec.md`](../project-layer/caller-workflow-spec.md)，
实例 [`../../projects/template/.github/workflows/caller-workflow.yml.tmpl`](../../projects/template/.github/workflows/)。

## 4. 跨 repo dispatch

骨架不能跨 repo 直接 `workflow_call`，故项目层通过 `repository_dispatch` 事件 type 触发：

- `event_type: requirement-analyze` → 骨架 1
- `event_type: implement-preview` → 骨架 2
- `event_type: release-deploy` → 骨架 3

## 5. 关联

- Runner：[`runners.md`](runners.md)
- 项目接线（A / B 档）：[`../project-layer/onboarding-tier-A.md`](../project-layer/onboarding-tier-A.md)、[`../project-layer/onboarding-tier-B.md`](../project-layer/onboarding-tier-B.md)
- 全景：[`../architecture.md`](../architecture.md)
