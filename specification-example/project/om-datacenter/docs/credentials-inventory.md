# 数据中台 — 凭据清单

> 本文件禁止出现真实凭据值。

## 1. 凭据表

| 名称                              | 档位          | 用途              | 注入位置                                      |
| --------------------------------- | ------------- | ----------------- | --------------------------------------------- |
| `DATACENTER_DB_PASSWORD`          | Vault sidecar | 业务库密码        | `vault.hashicorp.com/agent-inject-secret-...` |
| `DATACENTER_OAUTH_CLIENT_SECRET`  | K8s Secret    | OAuth2 客户端密钥 | `envFrom: secretRef`                          |
| `GITHUB_TOKEN_DATACENTER`         | GitHub Secret | 采集 GitHub 数据  | workflow env                                  |
| `GITEE_TOKEN_DATACENTER`          | GitHub Secret | 采集 Gitee 数据   | workflow env                                  |
| `GITCODE_TOKEN_DATACENTER`        | GitHub Secret | 采集 GitCode 数据 | workflow env                                  |
| `KAFKA_PASSWORD`                  | Vault sidecar | 事件 MQ 接入      | sidecar 注入                                  |
| `REDIS_PASSWORD`                  | K8s Secret    | 缓存              | envFrom                                       |
| `REGISTRY_USER` / `REGISTRY_PASS` | K8s Secret    | 镜像推送          | runner pod                                    |

## 2. 轮换计划

- 平台 token（GitHub / Gitee / GitCode）每 60 天轮换
- DB / Kafka 密码每 90 天轮换
- 检测到泄漏立即轮换 + 通知 secops

## 3. 关联

- 团队安全规范：[`../../../teams/standards/security.md`](../../../teams/standards/security.md)
- 通用凭据存储：[`../../../pipeline/generic-layer/credentials-storage.md`](../../../pipeline/generic-layer/credentials-storage.md)
- Gitleaks 门禁：[`../../../teams/security-gates/Gitleaks.md`](../../../teams/security-gates/Gitleaks.md)
