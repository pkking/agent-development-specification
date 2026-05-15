# 数据中台 — API 规约

> APIMagic 对外接口契约总入口。详细 OpenAPI 在 `APIMagic` 子仓 `openapi.yaml`。

## 1. 接口分组

| 分组       | 前缀               |
| ---------- | ------------------ |
| 社区元数据 | `/v1/communities`  |
| 贡献者数据 | `/v1/contributors` |
| 仓库指标   | `/v1/repos`        |
| 事件流     | `/v1/events`       |
| 聚合统计   | `/v1/metrics`      |

## 2. 主要接口

| Method | Path                         | 说明                       | 鉴权         |
| ------ | ---------------------------- | -------------------------- | ------------ |
| GET    | `/v1/communities`            | 列出已接入社区             | 公开         |
| GET    | `/v1/communities/{id}/repos` | 社区下仓库                 | 公开         |
| GET    | `/v1/contributors/{login}`   | 贡献者详情                 | OAuth2       |
| POST   | `/v1/events`                 | 上报事件（仅采集器内调用） | 服务间 token |
| GET    | `/v1/metrics/{repo}/qoq`     | 季度环比指标               | OAuth2       |

## 3. 错误码

| code                 | 含义       |
| -------------------- | ---------- |
| `INVALID_PARAM`      | 入参不合法 |
| `RESOURCE_NOT_FOUND` | 资源不存在 |
| `RATE_LIMITED`       | 触发限流   |
| `INTERNAL_ERROR`     | 内部错误   |

## 4. 关联

- 团队 API 设计规范：[`../../../teams/standards/api-design.md`](../../../teams/standards/api-design.md)
- API 安全：[`../../../teams/context/team/api-security.md`](../../../teams/context/team/api-security.md)
