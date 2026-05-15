# API 设计规范

## 1. 接口风格

- **REST**：资源用复数名词（`/users`、`/orders`），动作用 HTTP 方法
- **GraphQL**：仅在 BFF / 聚合层使用；不在域服务暴露
- **gRPC**：内部服务间通信优先选；`.proto` 必须 review

## 2. URL / 版本

- 所有公共 API 必须带版本前缀：`/v1/`、`/v2/`
- 不兼容变更必须升大版本；不允许「在 v1 偷偷改语义」

## 3. 入参 / 出参

| 项 | 规则 |
|---|---|
| 请求体 | JSON；字段 snake_case 或 camelCase 全仓统一（项目层定）|
| 错误响应 | `{ "code": "<machine_code>", "message": "<human>", "request_id": "<uuid>" }` |
| 分页 | `?page=<n>&page_size=<m>`；返回 `total`、`page`、`page_size` |
| 时间 | ISO 8601 + UTC（`2026-05-07T12:34:56Z`）|
| 钱 / 精度数值 | 字符串而非 float |

## 4. 安全

- 所有写接口必须鉴权（OAuth2 / JWT）；GET 也建议鉴权
- 敏感数据出参必须脱敏（手机号 / 身份证 / token）
- 限流策略见 [`../context/team/api-security.md`](../context/team/api-security.md)
- 输入校验：JSON schema 验证 + 业务规则验证，二选一不可省

## 5. 文档

- OpenAPI 3.x 必出；放在项目仓 `docs/api-spec.md` 或独立 `openapi.yaml`
- 模板见 [`../templates/`](../templates/)

## 6. 关联

- API 安全详尽：[`../context/team/api-security.md`](../context/team/api-security.md)、[`../context/team/API安全最佳实践.md`](../context/team/API安全最佳实践.md)
- 编码规范：[`coding.md`](coding.md)
