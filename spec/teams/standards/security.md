# 安全规范（团队级）

## 1. 不可违反的绝对禁令（提交前必查）

- 禁止任何形式的 **真实凭据 / 私钥 / token / 密码 / 内网 IP / 内部域名** 入仓
- 提交前必跑 [`../security-gates/Gitleaks.md`](../security-gates/Gitleaks.md) 描述的检测
- 已意外提交的凭据：**立即轮换** + 通知 secops，不仅是 `git rm`

## 2. 凭据存储

按 [`../../pipeline/generic-layer/credentials-storage.md`](../../pipeline/generic-layer/credentials-storage.md) 三档：

| 档位          | 用途                             | 注入方式                                           |
| ------------- | -------------------------------- | -------------------------------------------------- |
| GitHub Secret | CI 用 token / API key            | workflow `env:`                                    |
| K8s Secret    | 容器运行时                       | `envFrom: secretRef` / volume mount                |
| Vault sidecar | 高敏感凭据（DB root / 加密私钥） | `vault.hashicorp.com/agent-inject-secret-...` 注入 |

## 3. 安全编码

详尽规则见 [`../context/team/安全编码规范.md`](../context/team/安全编码规范.md) 与 [`../context/team/安全设计与开发最佳实践.md`](../context/team/安全设计与开发最佳实践.md)。要点：

- 参数化查询，禁止字符串拼 SQL / NoSQL filter / shell command
- 反序列化只接受已知类型白名单
- 文件上传：校验 MIME + 后缀 + magic number + 限制大小 + 隔离目录
- 身份认证：OAuth2 / OIDC；自研登录必须经安全 review

## 4. 自动门禁

每个 PR 必须通过：

- [`../security-gates/Gitleaks.md`](../security-gates/Gitleaks.md) — 凭据扫描
- [`../security-gates/SAST.md`](../security-gates/SAST.md) — 静态应用安全测试
- [`../security-gates/UT-coverage.md`](../security-gates/UT-coverage.md) — UT 覆盖率门槛

## 5. 应急

- 发现安全漏洞：**不开 issue** ；私下联系 secops 走 CVE 流程
- 生产事故：按 [`../templates/Learn From the Incident/`](../templates/Learn%20From%20the%20Incident/) 复盘
