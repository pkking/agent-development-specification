# 流程 3 — 合入 + 上线

> maintainer 评 `[<服务名>需求上线]` 触发（白名单）。合 PR + 部署 beta + 清理预览。

## 1. 触发

| 项 | 值 |
|---|---|
| 入口评论 | `[<服务名>需求上线]` |
| 谁可评 | maintainer 白名单（项目层声明） |
| 前置 | 流程 2 预览已起、PR 评审通过 |
| 跑在哪 | ai-dev-runner + k8s-deployer |

## 2. 步骤

1. 校验评论人在白名单（不在则拒绝并评论原因）
2. 合所有相关 PR（backlog 仓需求 PR + dev 仓实现 PR）
3. 触发部署到 beta namespace
4. 清理预览资源（按 deployer cleanup 规则）
5. 生成 release notes 片段（[`../../teams/prompts/release-notes.md`](../../teams/prompts/release-notes.md)）
6. 评论 issue：「已上线 beta → 灰度指引」

## 3. 灰度

- beta 部署后 24 h 值守期
- 任意金指标恶化 → 自动回滚（详见 [`../../teams/standards/release.md`](../../teams/standards/release.md)）
- 通过 24 h → 项目 release manager 手工触发生产灰度（不在自动流水线内）

## 4. 失败处理

- 合 PR 冲突 → 评论 PR + 标 `needs-rebase`
- beta 部署失败 → 不合 PR；评论原因
- 白名单校验失败 → 评论拒绝原因；不执行任何 merge

## 5. 关联

- 部署：[`../generic-layer/deployer.md`](../generic-layer/deployer.md)
- 团队发布规范：[`../../teams/standards/release.md`](../../teams/standards/release.md)
- Release notes：[`../../teams/prompts/release-notes.md`](../../teams/prompts/release-notes.md)
- 发布流程详细：[`../release-process.md`](../release-process.md)
