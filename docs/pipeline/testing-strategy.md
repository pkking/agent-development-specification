# 通用测试策略

> 整条流水线的测试编排策略，与团队层 [`../teams/standards/testing.md`](../teams/standards/testing.md) 相辅相成。

## 1. 分层

详见 [`generic-layer/tests.md`](generic-layer/tests.md)。流水线分层执行的本质：

```
PR 创建 / 更新
   ↓
ai-dev-runner 内：smoke + UT + interface contract（短反馈）
   ↓
k8s-deployer 部署预览
   ↓
预览 namespace 内：integration + e2e（长反馈，依赖真依赖）
   ↓
评论 PR：测试报告 + 覆盖率
```

## 2. 失败级联

| 失败层 | 后果 |
|---|---|
| smoke | 直接红，进 dev agent 修复轮 |
| UT | 红 + 覆盖率不达标进修复轮 |
| contract | 红，且 review agent 优先评审 |
| integration | 红，但预览 URL 仍可访问（人工调试） |
| e2e | 红，标 `needs-human` |

## 3. 覆盖率

UT 行覆盖率门槛由 [`../teams/security-gates/UT-coverage.md`](../teams/security-gates/UT-coverage.md) 定；
项目层可在 `.preview/service.yaml` 的 `coverage_threshold` 字段提高。

## 4. 关联

- 团队测试规范：[`../teams/standards/testing.md`](../teams/standards/testing.md)
- 测试经验沉淀：[`../teams/context/experience/测试策略编写经验.md`](../teams/context/experience/测试策略编写经验.md)
- 公共测试编排：[`generic-layer/tests.md`](generic-layer/tests.md)
