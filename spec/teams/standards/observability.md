# 可观测性规范

## 1. 日志

- 格式：JSON 单行；必含 `ts`、`level`、`request_id`、`service`、`msg`
- 级别：`debug` / `info` / `warn` / `error`；生产默认 `info`
- 不允许把 token / 密码 / 完整身份证 / 银行卡 写进日志
- 单条日志 ≤ 8 KB；超过截断

## 2. 指标

- 命名 `<service>_<subject>_<unit>`，如 `api_request_duration_seconds`
- 必采 4 个金指标：QPS / 错误率 / P99 延迟 / 饱和度（CPU / mem / 连接池）
- Prometheus pull 模型；scrape interval 15 s

## 3. 追踪

- 跨服务必传 `trace_id` / `span_id` header（W3C TraceContext）
- 采样率：生产默认 1%；故障期临时调到 100%

## 4. 告警

- 阈值告警必须有 runbook 链接；无 runbook 的告警禁止上生产
- 告警分级：P0（人值守 5 min 响应）/ P1（1 h）/ P2（次工作日）
- 误报率 > 30% 必须重写规则或下线

## 5. Dashboard

- 每个服务必有 Grafana / 等价工具的「服务健康总览」面板
- 项目层在 `docs/deployment.md` 写明 dashboard 链接（如有内部链接，仅团队访问，不入文档仓正文）

## 6. 关联

- 团队故障复盘模板：[`../templates/Learn From the Incident/`](../templates/Learn%20From%20the%20Incident/)
- 安全审计日志要求：[`security.md`](security.md)
