# Generic Layer — Deployer

> 把构建产物起到 K8s 预览 namespace（流程 2）/ 推到 beta（流程 3）/ 清理预览（PR 关闭时）。这一份是 deploy 的**单文档完整入口**。
> 代码：[`../../src/deployer/`](../../src/deployer/)。

## 1. 它在流水线里站在哪

```
流程 2 内的对抗循环：
  design → dev → 【deploy】 → review + tester → feedback → (回 dev 重跑)
                    ↑
               本文档讲的就是这一步

流程 3：
  merge PRs → 【deploy.py promote】 → 【deploy.py cleanup】
                    ↑                       ↑
               推 beta 触发 Jenkins      删 PR 预览资源
```

deploy **不是 agent，是脚本** — orchestrate.sh 在 dev 之后、review/tester 之前调它。失败直接算这一轮失败，把 `report` 字段带给 tester 作打回输入。

## 2. 4 种部署模式

由项目仓 `.preview/service.yaml` 中的 `deploy_mode` 字段声明（规范：[`../project-layer/preview-service-yaml-spec.md`](../project-layer/preview-service-yaml-spec.md)）。

| 模式 | 适用 | 资源策略 | 例子 |
|---|---|---|---|
| `dev-pod` | 单 PR 独立后端服务 | Deployment + Service + Ingress，每 PR 一组；PR 关后清掉 | APIMagic per-PR |
| `data-pod` | 含状态（DB / cache / Vector store） | + StatefulSet + PVC；清理时保留 PVC 一段时间防误删 | om-dataarts 采集任务 |
| `shared` | 多 PR 共享 1 个 deployment + 不同 URL 前缀 | 只换镜像不改 svc / ingress | datastat 前端预览 |
| `none` | 纯工具仓 / 文档仓 / 不需部署 | 跳过；只跑 build + 单测 | om-deployment、om-dataarts-deployment |

**选错怎么办**：选错只影响预览资源回收，安全无虞。`none` 永远是兜底选项。

## 3. deploy.py 入参 / 出参

代码：[`../../src/deployer/deploy.py`](../../src/deployer/deploy.py)

### 入参

| 参数 | 必填 | 说明 |
|---|---|---|
| `--project` | ✓ | 项目名（决定 namespace / 模板路径） |
| `--service` | ✓ | 服务名（一个项目可能多服务） |
| `--mode` | ✓ | `dev-pod` / `data-pod` / `shared` / `none` |
| `--image` | ✓ | 已推到 registry 的镜像全名（含 tag） |
| `--pr-number` | ✓ | PR 号（生成唯一 svc 名 + 预览域名） |
| `--namespace` | ✓ | 目标 namespace |
| `--base-domain` | 可选 | 预览域名后缀（默认从 env `BASE_DOMAIN`） |
| `--config` | 可选 | 服务 YAML 路径（默认 `.preview/service.yaml`） |
| `--cleanup` | 可选 flag | 不部署，反向删除（PR 关闭时用） |

### 输出（写到 stdout，orchestrate.sh 重定向到 `/tmp/opencode/deploy/pr-<N>.json`）

```jsonc
{
  "pr_number": 41,
  "preview_url": "https://apimagic-41.ai.test.osinfra.cn/",
  "cluster_ip_service": "preview-apimagic-pr41.ai-test.svc.cluster.local:9999",
  "ready": true,            // false = readiness 超时 / apply 失败
  "report": "...",          // 失败时的关键日志摘要（apply 错误 / pod logs tail / readinessProbe 失败原因）
  "deploy_mode": "dev-pod",
  "applied_resources": [
    {"kind": "Deployment", "name": "preview-apimagic-pr41"},
    {"kind": "Service",    "name": "preview-apimagic-pr41"},
    {"kind": "Ingress",    "name": "preview-apimagic-pr41"}
  ],
  // mode 特定的附加字段（按模式扩展）：
  "apimagic_endpoints": [{ "file": "...", "method": "GET", "path": "/...", "url": "..." }],
  "apimagic_table": "magic_api_file_v2_pr41"
}
```

### 退出码

| 码 | 含义 |
|---|---|
| 0 | apply 成功 + readiness 就绪 |
| 2 | 入参不合法（如 mode 不在 4 选 1） |
| 3 | kubectl apply 失败 |
| 4 | readiness 等待超时 |
| 99 | 内部错误 |

## 4. 详细部署流程

```
1. 读 .preview/service.yaml      读 deploy_mode / image / port / health_check / ingress / namespace / env / resources
2. 选模板                          按 mode → src/deployer/templates/<mode>/*.yaml
3. 渲染                            替换 ${PROJECT} / ${SERVICE} / ${PR_NUMBER} / ${IMAGE_FULL} / ${NAMESPACE} / ${BASE_DOMAIN}
                                  渲染产物落到 src/deployer/.rendered/<project>-<service>-pr<N>/
4. kubectl apply                  按渲染产物逐个 apply
5. kubectl wait                   等 Deployment readiness（默认 120s）
6. 收集预览 URL + Service ClusterIP + pod 状态 → 输出 JSON
7. 失败 → 收集 kubectl describe / pod logs tail 进 report 字段
```

## 5. K8s 模板

每个 mode 一套 K8s yaml（**spec 仓 stub，生产仓按需扩展**）：

| 路径 | 含 | 何时用 |
|---|---|---|
| [`../../src/deployer/templates/dev-pod/`](../../src/deployer/templates/) | Deployment + Service + Ingress | 单 PR 独立后端 |
| [`../../src/deployer/templates/data-pod/`](../../src/deployer/templates/) | + StatefulSet + PVC | 含状态服务 |
| [`../../src/deployer/templates/shared/`](../../src/deployer/templates/) | 只是 image 替换 patch | 多 PR 共享后端 |

模板占位符：`${PROJECT}` / `${SERVICE}` / `${PR_NUMBER}` / `${IMAGE_FULL}` / `${NAMESPACE}` / `${BASE_DOMAIN}`。

## 6. 预览资源命名约定

| 资源 | 名字 |
|---|---|
| Deployment / StatefulSet | `preview-<service>-pr<N>` |
| Service | 同上 |
| Ingress | 同上；host 形如 `<service>-<N>.<base-domain>` |
| PVC（仅 data-pod） | `preview-<service>-pr<N>-data` |
| Label | `app=preview, service=<service>, pr=<N>` |

orchestrate.sh / tester 用这套命名规则查/直连资源（如 `kubectl exec deployment/preview-apimagic-pr41 ...`）。

## 7. 清理 / 回收

3 条路径：

| 触发 | 动作 |
|---|---|
| PR 关闭 / 合并 → 项目仓 caller workflow → 派 `pr_deploy_cleanup` 事件 → k8s-deployer | `deploy.py --cleanup --pr-number <N>` 删 Deployment / Service / Ingress（data-pod 保留 PVC 7 天） |
| 流程 3 上线 beta 后 | 在 issue-3 yml step 6 跑 `deploy.py --cleanup` 清相关 PR 预览 |
| 定时兜底 | `cleanup-cron.yaml` 每日扫 `pr=` label，对应 PR 已关 ≥ 7 天则强删（含 PVC） |

## 8. promote 到 beta（流程 3 用）

`deploy.py promote --env beta --service <X>` — 触发 Jenkins job（不是直接 `kubectl apply`，因为 beta 镜像由独立 build pipeline 出）。需 `JENKINS_API_USER` + [`JENKINS_API_TOKEN`](credentials-storage.md)。

详细：[`../stage-flow/flow-3-release.md`](../stage-flow/flow-3-release.md)。

## 9. 哪个 runner 跑这个脚本

| 调用方 | runner |
|---|---|
| 流程 2 的对抗循环（orchestrate.sh 调 deploy.py） | `ai-dev-runner`（KUBECONFIG 注入到 runner pod） |
| 旁支 PR preview workflow（PR opened / synchronize / closed） | `k8s-deployer`（专门跑 deploy / cleanup 的 runner，权限更宽，见 [`runners.md` §3](runners.md#3-k8s-deployer)） |
| 流程 3 的 promote / cleanup | `ai-dev-runner` |

为什么不全用 k8s-deployer？因为 ai-dev-runner 已经持有 deploy 用的 kubeconfig + 上下文，少一次跨 pod 跳转。仅在「不能给 ai-dev-runner 那么大权限」的部署场景才必须 k8s-deployer。

## 10. 关联

- 模板渲染依赖：[`../project-layer/preview-service-yaml-spec.md`](../project-layer/preview-service-yaml-spec.md)
- Runner：[`runners.md`](runners.md)
- 凭据：[`credentials-storage.md`](credentials-storage.md)
- 4 项门禁（在 deploy 之前，跑 dev 产物）：[`gates.md`](gates.md)
- tester 角色（消费 deploy 的输出）：[`../../teams/prompts/tester.md`](../../teams/prompts/tester.md)
