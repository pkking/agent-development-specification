# k8s-deployer

> Self-hosted GitHub Actions runner，标签 `[self-hosted, k8s-deployer]`，跑在 K8s 集群里。**专门跑 deploy.py 起 / 清 / promote 预览**。
>
> 两个 runner 的对比和共性说明见 [../README.md](../README.md)。

## 为什么单独一类 runner

- ai-dev-runner 拿不到目标 namespace 的 `deployments / services / ingresses / pvc` create-update-delete 权限（最小权限）
- k8s-deployer 才有这套 ClusterRole（见 [`rbac.yaml`](rbac.yaml)）
- 两个 runner 用不同的 RBAC 边界

## 镜像里装了什么（比 ai-dev-runner 少）

详见 [Dockerfile](Dockerfile)。摘要：

- Ubuntu 24.04
- 系统包：`git curl wget jq python3 sudo`（**没装 Node / Java / Claude CLI / build-essential**，只跑 deploy）
- K8s 工具：`kubectl` + `helm`
- GitHub Actions Runner：`actions/runner` v2.317.0
- 非 root 用户 `deployer`

## 快速开始

### 构建镜像

```bash
# 本地
REGISTRY=registry.example.com/team ./build-and-push.sh

# 或通过 GitHub Actions 手动触发（推荐）
# Actions → Build Runner Images → Run workflow → 选 k8s-deployer
```

### 部署

```bash
kubectl create ns ci-runners

kubectl -n ci-runners create secret generic k8s-deployer-secrets \
    --from-literal=GH_RUNNER_TOKEN=<...> \
    --from-literal=JENKINS_API_USER=<...> \
    --from-literal=JENKINS_API_TOKEN=<...>

kubectl -n ci-runners create secret generic deployer-kubeconfig \
    --from-file=config=/path/to/kubeconfig

kubectl apply -f rbac.yaml         # 注意是 ClusterRole/Binding
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml

# 验证
kubectl -n ci-runners get pod -l app=k8s-deployer
# GitHub Settings → Actions → Runners 应看到 N 个 online
```

## 必须的 Token / 配置

### ConfigMap（非敏感）— [`configmap.yaml`](configmap.yaml)

| 字段       | 必填 | 含义                       |
| ---------- | ---- | -------------------------- |
| `GH_OWNER` | ✓    | runner 注册到的 GitHub Org |
| `GH_REPO`  | ✓    | runner 注册到的仓库        |

### Secret（敏感，**不入仓**）

| Secret 字段                                                      | 必填              | 用途                       | 从哪拿                                                        |
| ---------------------------------------------------------------- | ----------------- | -------------------------- | ------------------------------------------------------------- |
| `GH_RUNNER_TOKEN`                                                | ✓                 | 注册 self-hosted runner    | GitHub: Settings → Actions → Runners → New self-hosted runner |
| `AI_TEST_KUBECONFIG`（挂为 `deployer-kubeconfig` Secret volume） | ✓                 | kubectl 操作目标 namespace | 集群 admin                                                    |
| `JENKINS_API_USER` / `JENKINS_API_TOKEN`                         | 流程 3 promote 时 | 触发 Jenkins job 上 beta   | Jenkins admin                                                 |

**不需要** `ANTHROPIC_API_KEY` / `OPENCODE_API_KEY` / `BACKLOG_REPO_TOKEN`（这里只跑 deploy 脚本，不跑 agent）。

## RBAC（关键差异）

[`rbac.yaml`](rbac.yaml) 用 **ClusterRole + ClusterRoleBinding**（不是 namespaced Role）：

| 资源                                                        | 权限                                |
| ----------------------------------------------------------- | ----------------------------------- |
| `apps/deployments`、`apps/statefulsets`、`apps/replicasets` | get/list/create/update/patch/delete |
| `services`、`configmaps`、`persistentvolumeclaims`、`pods`  | 同上                                |
| `networking.k8s.io/ingresses`                               | 同上                                |

生产建议：用 namespace-scoped RoleBinding 限定到 `ai-test` / `ai-beta` 等专用 namespace，不要给全集群。

## 为什么 k8s-deployer 不挂 docker.sock

不 build 镜像，只 `kubectl apply`，所以**不需要挂** `/var/run/docker.sock`。安全面比 ai-dev-runner 小很多。

## 在流水线里跑哪些事

| 调用源                                              | 命令                                                     |
| --------------------------------------------------- | -------------------------------------------------------- |
| 旁支 PR preview workflow（PR opened / synchronize） | `python3 deploy.py --project=... --pr-number=...` 起预览 |
| 旁支 PR preview workflow（PR closed）               | `python3 deploy.py --cleanup --pr-number=...` 删预览     |
| 流程 3 cleanup 阶段                                 | 同 cleanup                                               |

## 本地调试

```bash
export GH_OWNER=<org> GH_REPO=<repo> GH_RUNNER_TOKEN=<token> KUBECONFIG_FILE=/path/to/kubeconfig
./start-runner.sh
```

## 文件清单

| 文件                                       | 作用                                         |
| ------------------------------------------ | -------------------------------------------- |
| [Dockerfile](Dockerfile)                   | 镜像定义                                     |
| [entrypoint.sh](entrypoint.sh)             | 容器入口：注册 runner → 监听 job             |
| [start-runner.sh](start-runner.sh)         | 本地调试入口                                 |
| [build-and-push.sh](build-and-push.sh)     | 构建脚本                                     |
| [deployment.yaml](deployment.yaml)         | K8s Deployment（含 kubeconfig volume mount） |
| [rbac.yaml](rbac.yaml)                     | **ClusterRole** + ClusterRoleBinding         |
| [configmap.yaml](configmap.yaml)           | 非敏感配置                                   |
| [secret-example.yaml](secret-example.yaml) | Secret 字段示例                              |
