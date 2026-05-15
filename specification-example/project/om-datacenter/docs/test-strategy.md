# 数据中台 — 测试策略

> 项目层测试策略。

## 1. 分层范围

| 层          | 范围                        | 跑哪           | 时长上限 |
| ----------- | --------------------------- | -------------- | -------- |
| smoke       | 跨子仓基本启动              | ai-dev-runner  | 5 min    |
| UT          | 各子仓内部                  | ai-dev-runner  | 10 min   |
| contract    | APIMagic ↔ datastat 接口    | ai-dev-runner  | 5 min    |
| integration | om-dataarts + APIMagic + DB | 预览 namespace | 20 min   |
| e2e         | 用户访问 datastat 完整链路  | 预览 namespace | 30 min   |

## 2. 覆盖率门槛

- 行覆盖率：≥ 65%（高于团队 60% 基线）
- API 黄金路径分支覆盖率：≥ 90%

## 3. 测试环境

- smoke / UT / contract → ai-dev-runner 容器
- integration / e2e → 预览 namespace `ai-test`

## 4. 用例索引

- 元数据采集回归：`om-dataarts/test/regression/`
- API 契约：`APIMagic/test/contract/`
- 前端 e2e：`datastat-manage-website/cypress/`

## 5. 关联

- 团队测试规范：[`../../../teams/standards/testing.md`](../../../teams/standards/testing.md)
