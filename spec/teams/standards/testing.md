# 测试规范

## 1. 分层

| 层                 | 目的              | 跑在哪             | 时长上限 |
| ------------------ | ----------------- | ------------------ | -------- |
| smoke              | PR 必跑、快速反馈 | `ai-dev-runner` 内 | 5 min    |
| unit (UT)          | 函数 / 类粒度     | `ai-dev-runner` 内 | 10 min   |
| interface contract | 跨服务 API 契约   | `ai-dev-runner` 内 | 5 min    |
| integration        | 依赖真 DB / 下游  | 预览环境           | 20 min   |
| e2e                | 黄金链路          | 预览环境           | 30 min   |

详见 [`../../pipeline/generic-layer/tests.md`](../../pipeline/generic-layer/tests.md)。

## 2. 覆盖率

- 单元测试行覆盖率 ≥ 60%（团队基线）；项目可在 `docs/test-strategy.md` 提高
- 关键路径分支覆盖率 ≥ 80%
- 门禁见 [`../security-gates/UT-coverage.md`](../security-gates/UT-coverage.md)

## 3. 写法

- **AAA**：Arrange / Act / Assert，每个 test 一段断言
- 测试名描述行为：`test_login_with_wrong_password_returns_401`
- 不允许跨用例共享可变状态
- mock 边界（外部 API / DB），不 mock 自家代码

## 4. 测试数据

- 用 factory + fixture，不在 repo 内塞大文件
- 敏感数据全用假数据；禁止从生产 dump
- 模板见 [`../templates/`](../templates/)

## 5. 关联

- 测试策略写法：[`../templates/Test/#1 Test Strategy.md`](../templates/Test/%231%20Test%20Strategy.md)
- 测试经验：[`../context/experience/`](../context/experience/)
