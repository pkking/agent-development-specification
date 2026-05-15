# 发布规范

## 1. 版本号

`MAJOR.MINOR.PATCH`（SemVer）：

- MAJOR — 不兼容 API 变更
- MINOR — 向下兼容新功能
- PATCH — 向下兼容 bug 修复

`v` 前缀必加：`v1.2.3`。

## 2. 发布流程

| 阶段 | 触发                               | 动作                              |
| ---- | ---------------------------------- | --------------------------------- |
| 预览 | PR 创建 / 更新                     | 自动起预览 URL（流水线流程 2）    |
| beta | `[<服务名>需求上线]`（白名单评论） | 合 PR + 部署 beta（流水线流程 3） |
| 生产 | 人工触发（release manager）        | 走单独 release workflow + 灰度    |

详见 [`../../pipeline/architecture.md`](../../pipeline/architecture.md) 流程 3 段。

## 3. Release notes

每次合 PR 必生成 release notes 片段，模板见 [`../templates/Release/`](../templates/Release/)；
AI 辅助生成见 [`../prompts/release-notes.md`](../prompts/release-notes.md)。

## 4. 灰度

- 生产发布默认 5% → 25% → 100%，每档观察 ≥ 1 h
- 任意金指标恶化 ≥ 阈值 → 自动回滚
- 回滚演练每季度至少 1 次

## 5. 上线后

- 24 h 内值守，可观测性面板见 [`observability.md`](observability.md)
- 出事故按 [`../templates/Learn From the Incident/`](../templates/Learn%20From%20the%20Incident/) 复盘

## 6. 关联

- git 分支策略：[`git-workflow.md`](git-workflow.md)
- 发布过程总览：[`../../pipeline/release-process.md`](../../pipeline/release-process.md)
