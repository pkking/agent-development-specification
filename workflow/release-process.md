# 通用发布流程

> 流程 3「合入 + 上线」之后的完整发布过程；与团队层 [`../teams/standards/release.md`](../teams/standards/release.md) 相辅相成。

## 1. 全流程

```
流程 3 评论触发
   ↓
白名单校验
   ↓
合所有相关 PR（backlog 需求 PR + dev 实现 PR）
   ↓
触发 beta 部署（k8s-deployer）
   ↓
24 h beta 值守
   ├─ 金指标稳定 → 项目 release manager 手动触发生产
   └─ 任意金指标恶化 → 自动回滚（详见 release.md）
   ↓
生产灰度（5% → 25% → 100%，每档观察 ≥ 1h）
   ↓
release notes 自动生成（teams/prompts/release-notes.md）
   ↓
归档：events / metrics / dashboard 快照
```

## 2. 自动 vs 人工

| 阶段                   | 自动               | 人工                |
| ---------------------- | ------------------ | ------------------- |
| 合 PR                  | ✅                 | —                   |
| beta 部署              | ✅                 | —                   |
| beta 灰度（24 h 值守） | 监控 + 回滚        | 决策是否进生产      |
| 生产灰度               | 灰度比例切换       | 触发 + 决策每档继续 |
| 回滚                   | ✅（金指标恶化时） | —                   |
| 复盘                   | —                  | ✅（出事故时）      |

## 3. 复盘

任何生产事故按 [`../teams/templates/Learn From the Incident/`](../teams/templates/Learn%20From%20the%20Incident/) 模板。

## 4. 关联

- 流程 3：[`stage-flow/flow-3-release.md`](stage-flow/flow-3-release.md)
- **生产发布治理（release-mgmt：变更计划 + 同意发布门禁）**：[`change-release-process.md`](change-release-process.md)
- 团队发布规范：[`../teams/standards/release.md`](../teams/standards/release.md)
- 部署器：[`generic-layer/deployer.md`](generic-layer/deployer.md)
