# #1 Test Specification

> 用例规约 — 描述「单条用例怎么写」，给具体的 case 写作者参考。
> 与同目录的 [`#1 Test Strategy.md`](#1%20Test%20Strategy.md)（整体策略） / [`#1 Test Report.md`](#1%20Test%20Report.md)（执行报告）配套使用。

## 1. 用例命名

`<被测能力>-<前置条件>-<预期结果>`，如 `login-with-wrong-password-returns-401`。

## 2. 每条用例必含字段

| 字段 | 说明 |
|---|---|
| 用例 ID | 全仓唯一，建议带模块前缀，如 `auth.login.001` |
| 对应 task(issueID) 链接 | `<issue-url>`（指向 backlog 仓 issue） |
| 前置条件 | 数据 / 环境 / 依赖服务状态 |
| 操作步骤 | 编号步骤，每步一行 |
| 预期结果 | 可观察、可断言（HTTP 状态码 / DB 行数 / 日志内容） |
| 优先级 | P0 / P1 / P2 |
| 类型 | smoke / unit / integration / interface contract / e2e |

## 3. 用例分层

- **smoke**：每次 PR 必跑，5 分钟内完成 — 详见 [`../../security-gates/`](../../security-gates/) 与团队测试规范 [`../../standards/testing.md`](../../standards/testing.md)
- **unit (UT)**：覆盖率门禁见 [`../../security-gates/UT-coverage.md`](../../security-gates/UT-coverage.md)
- **interface contract**：跨服务接口契约（Pact / OpenAPI schema 对比）
- **integration**：依赖真实 DB / 真实下游，跑在预览环境
- **e2e**：跑在预览环境，仅核心黄金链路

## 4. 关联

- 整体策略写法 → [`#1 Test Strategy.md`](#1%20Test%20Strategy.md)
- 执行报告写法 → [`#1 Test Report.md`](#1%20Test%20Report.md)
- 测试经验沉淀 → [`../../context/experience/`](../../context/experience/)
- 通用流水线测试编排 → [`../../../pipeline/generic-layer/tests.md`](../../../pipeline/generic-layer/tests.md)

