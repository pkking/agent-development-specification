# Generic Layer — 凭据存储

> 流水线用到的所有凭据三档存储 + 注入方式。

## 1. 三档分类

| 档位               | 用途                                 | 注入方式                                                                     |
| ------------------ | ------------------------------------ | ---------------------------------------------------------------------------- |
| GitHub Secret      | CI / runner 启动期需要的 token       | workflow `env:` 或 runner pod 的 `secretRef`                                 |
| K8s Secret         | 容器运行时 long-lived 凭据           | `envFrom: secretRef` / `volumeMounts`                                        |
| Vault sidecar 注入 | 高敏感凭据（DB root 密码、加密私钥） | `vault.hashicorp.com/agent-inject-secret-application.yml: internal/data/...` |

## 2. 凭据清单（流水线层）

| 名称                              | 档位                          | 用途                                     |
| --------------------------------- | ----------------------------- | ---------------------------------------- |
| `GITHUB_TOKEN`                    | GitHub Secret（org 级）       | gh CLI / API 调用，必含 `workflow` scope |
| `GITCODE_TOKEN`                   | GitHub Secret                 | 镜像源代码同步到 GitCode                 |
| `ANTHROPIC_API_KEY`               | GitHub Secret + K8s Secret    | runner 内 Claude CLI                     |
| `ANTHROPIC_BASE_URL`              | configmap                     | runner 内 Claude endpoint                |
| `ANTHROPIC_MODEL`                 | configmap                     | runner 内 model id                       |
| `REGISTRY_USER` / `REGISTRY_PASS` | K8s Secret（runner 用）       | 推镜像到 registry                        |
| `KUBECONFIG`                      | K8s Secret（k8s-deployer 用） | 调 k8s API                               |
| `VAULT_TOKEN`                     | K8s Secret                    | 启 vault sidecar                         |

## 3. 项目层凭据清单

每个项目在 `projects/<project>/docs/credentials-inventory.md` 中列自己额外用到的凭据 + 档位；
模板见 [`../../projects/template/docs/credentials-inventory.md.tmpl`](../../projects/template/docs/credentials-inventory.md.tmpl)。

## 4. 严禁

- 凭据明文写入仓库（包括 `.env`、`.tmpl`、注释、PR 描述）
- 把 K8s Secret 直接 cat 到日志 / PR 评论
- 用同一个 token 跨多项目（必须 1 项目 1 token，便于审计 + 轮换）

## 5. 轮换

- 检测到泄漏 → 立即轮换 + 通知 secops；不仅是 `git rm`
- 例行轮换：每 90 天对 long-lived token 强制轮换

## 6. 关联

- 团队安全规范：[`../../teams/standards/security.md`](../../teams/standards/security.md)
- Gitleaks 门禁：[`../../teams/security-gates/Gitleaks.md`](../../teams/security-gates/Gitleaks.md)
