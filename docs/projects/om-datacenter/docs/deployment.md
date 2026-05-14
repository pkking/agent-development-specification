# 数据中台 — 部署文档

## 1. 部署模式

| 子仓 | 模式 | 备注 |
|---|---|---|
| `datastat-manage-website` | `shared` | 静态文件，多 PR 共享 |
| `APIMagic` | `dev-pod` | 每 PR 独立 |
| `om-dataarts` | `data-pod` | 带 DB / 缓存 |
| `om-deployment` | `none` | 工具仓，不部署 |
| `om-dataarts-deployment` | `none` | 工具仓 |

## 2. K8s 资源

- 资源 yaml：[`../k8s/`](../k8s/)
- 各子仓 service.yaml：在各子仓的 [`.preview/service.yaml`](../../../pipeline/project-layer/preview-service-yaml-spec.md)

## 3. 环境

| 环境 | namespace | 域名 |
|---|---|---|
| 预览 | `ai-test` | `pr-<n>.ai.test.osinfra.cn` |
| beta | `ai-beta` | `beta.ai.osinfra.cn` |
| 生产 | `ai-prod` | `datastat.osinfra.cn` |

## 4. RPO / RTO

- 数据采集任务：RPO 24 h（次日补采）/ RTO 4 h
- API 服务：RPO 0 / RTO 30 min（热备）

## 5. 灰度策略

按团队默认（5% → 25% → 100%）。

## 6. Dashboard

内部 Grafana 面板（不对外）。

## 7. 关联

- 团队发布规范：[`../../../teams/standards/release.md`](../../../teams/standards/release.md)
