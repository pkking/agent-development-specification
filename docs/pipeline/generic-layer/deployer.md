# Generic Layer — Deployer

> 把构建产物部署到 K8s。代码：[`../../src/deployer/`](../../src/deployer/)。

## 1. 4 种部署模式

| 模式 | 适用 | 资源策略 |
|---|---|---|
| `dev-pod` | 单个开发 PR 起独立 pod + svc + ingress | 每 PR 一组资源，PR 关后自动清 |
| `data-pod` | 含状态（DB / cache）的服务 | 每 PR 一组带 PVC 的 pod；清理时保留 PVC 一段时间 |
| `shared` | 多 PR 共享一个 deployment + 不同路径前缀 | 节省资源；只换镜像不改 svc / ingress |
| `none` | 仅做 build / 单元测试，不实际部署 | 适合纯前端 / 工具仓 |

## 2. 模式选择

由项目仓 `.preview/service.yaml` 中的 `deploy_mode` 字段声明；
模板见 [`../project-layer/preview-service-yaml-spec.md`](../project-layer/preview-service-yaml-spec.md)。

## 3. 部署流程

```
ai-dev-runner 构建镜像并推到 registry
        ↓
ai-dev-runner 通过 repository_dispatch 触发 k8s-deployer
        ↓
k8s-deployer 调 deploy.py
        ↓
deploy.py 渲染 K8s 模板（按 deploy_mode 选模板）+ kubectl apply
        ↓
k8s-deployer 等 readiness 就绪
        ↓
回写预览 URL 到 PR 评论
```

## 4. deploy.py 入参

| 参数 | 说明 |
|---|---|
| `--project` | 项目名（决定 namespace / 模板路径） |
| `--service` | 服务名（一个项目可能多服务） |
| `--mode` | `dev-pod` / `data-pod` / `shared` / `none` |
| `--image` | 已推到 registry 的镜像全名 |
| `--pr-number` | PR 号（用于生成唯一 svc 名 + 预览域名） |
| `--namespace` | 目标 namespace |
| `--config` | 服务 YAML 路径（默认 `.preview/service.yaml`） |

## 5. K8s 模板

按 mode 选模板：

- [`../../src/deployer/templates/dev-pod/`](../../src/deployer/templates/) — Deployment + Service + Ingress
- [`../../src/deployer/templates/data-pod/`](../../src/deployer/templates/) — + StatefulSet + PVC
- [`../../src/deployer/templates/shared/`](../../src/deployer/templates/) — 仅 patch 已有 Deployment image

模板渲染规则：占位符 `${PROJECT}` / `${SERVICE}` / `${PR_NUMBER}` / `${IMAGE}` / `${BASE_DOMAIN}` / `${NAMESPACE}` 由 deploy.py 替换。

## 6. 清理

- PR 关闭 / 合并 → 触发 cleanup workflow → 调 `deploy.py --cleanup`
- 孤儿资源（PR 已关 7 天但资源还在）由 `cleanup-cron.yaml` 每日扫一次

## 7. 关联

- Runners：[`runners.md`](runners.md)
- 项目层 service.yaml 规范：[`../project-layer/preview-service-yaml-spec.md`](../project-layer/preview-service-yaml-spec.md)
- 凭据：[`credentials-storage.md`](credentials-storage.md)
