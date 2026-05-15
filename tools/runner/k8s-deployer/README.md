# k8s-deployer

> Self-hosted GitHub Actions runner，标签 `[self-hosted, k8s-deployer]`，跑在 K8s 集群里。**专门跑 deploy.py 起 / 清 / promote 预览**（旁支 PR preview workflow 主要用它；流程 2 / 3 内的 deploy 由 ai-dev-runner 跑，见下）。
>
> **完整文档**：[`../../../pipeline/generic-layer/runners.md`](../../../pipeline/generic-layer/runners.md) + [`../../../pipeline/generic-layer/deployer.md`](../../../pipeline/generic-layer/deployer.md)。

## 为什么单独一类 runner

- ai-dev-runner 拿不到目标 namespace 的 `deployments / services / ingresses / pvc` create-update-delete 权限（最小权限）
- k8s-deployer 才有这套 ClusterRole（见 [`rbac.yaml`](rbac.yaml)）
- 两个 runner 用不同的 RBAC 边界

## 镜像里装了什么（比 ai-dev-runner 少）

详见 [Dockerfile](Dockerfile)。摘要：

- Ubuntu 24.04
- 系统包：`git curl wget jq python3 sudo`（注意：**没装 Node / Java / Claude CLI / build-essential**，只跑 deploy）
- K8s 工具：`kubectl` + `helm`
- GitHub Actions Runner：`actions/runner` v2.317.0
- 非 root 用户 `deployer`

完整对照：[runners.md §3.3](../../../pipeline/generic-layer/runners.md#33-镜像组件清单差异处)。

## 必须的 Token / 配置

### ConfigMap（非敏感）— [`configmap.yaml`](configmap.yaml)

| 字段       | 必填 | 含义                       |
| ---------- | ---- | -------------------------- |
| `GH_OWNER` | ✓    | runner 注册到的 GitHub Org |
| `GH_REPO`  | ✓    | runner 注册到的仓库        |

### Secret

| Secret 字段                                                                                                                                                              | 必填              | 用途                              | 从哪拿                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------- | --------------------------------- | ------------------------------------------------------------- |
| [`GH_RUNNER_TOKEN`](../../../pipeline/generic-layer/credentials-storage.md)                                                                                              | ✓                 | 注册 self-hosted runner           | GitHub: Settings → Actions → Runners → New self-hosted runner |
| [`AI_TEST_KUBECONFIG`](../../../pipeline/generic-layer/credentials-storage.md)（挂为 `deployer-kubeconfig` Secret 的 volume，详见 [`deployment.yaml`](deployment.yaml)） | ✓                 | kubectl 操作目标 namespace 的权限 | 集群 admin                                                    |
| `JENKINS_API_USER` / [`JENKINS_API_TOKEN`](../../../pipeline/generic-layer/credentials-storage.md)                                                                       | 流程 3 promote 时 | 触发 Jenkins job 上 beta          | Jenkins admin                                                 |

**不需要** [`ANTHROPIC_API_KEY`](../../../pipeline/generic-layer/credentials-storage.md) / `OPENCODE_API_KEY` / `BACKLOG_REPO_TOKEN`（这里只跑 deploy 脚本，不跑 agent）。

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
| 流程 3 cleanup 阶段（也可以转给它跑）               | 同 cleanup                                               |

流程 2 / 3 内的 deploy 默认还是由 **ai-dev-runner** 跑（因为它已经有 KUBECONFIG + 上下文）；只在「不能给 ai-dev-runner 那么大权限」的项目场景才必须 k8s-deployer。详见 [deployer.md §9](../../../pipeline/generic-layer/deployer.md#9-哪个-runner-跑这个脚本)。

## 部署步骤

1. **建镜像**：`REGISTRY=<your-registry>/<your-team> ./build-and-push.sh`
2. **拿 runner registration token**：GitHub Settings → Actions → Runners
3. **建 namespace + Secret + kubeconfig**：
   ```bash
   kubectl create ns ci-runners
   kubectl -n ci-runners create secret generic k8s-deployer-secrets \
       --from-literal=GH_RUNNER_TOKEN=<...> \
       --from-literal=JENKINS_API_USER=<...> \
       --from-literal=JENKINS_API_TOKEN=<...>
   kubectl -n ci-runners create secret generic deployer-kubeconfig \
       --from-file=config=/path/to/kubeconfig
   ```
4. **apply yaml**：
   ```bash
   kubectl apply -f rbac.yaml         # 注意是 ClusterRole/Binding
   kubectl apply -f configmap.yaml
   kubectl apply -f deployment.yaml
   ```
5. **验证**：`kubectl -n ci-runners get pod -l app=k8s-deployer`；GitHub Settings → Actions → Runners 看到 N 个 online。

## 文件清单

| 文件                                       | 作用                                                                             |
| ------------------------------------------ | -------------------------------------------------------------------------------- |
| [Dockerfile](Dockerfile)                   | 镜像定义                                                                         |
| [entrypoint.sh](entrypoint.sh)             | 容器入口                                                                         |
| [start-runner.sh](start-runner.sh)         | 本地调试入口                                                                     |
| [build-and-push.sh](build-and-push.sh)     | 构建脚本                                                                         |
| [deployment.yaml](deployment.yaml)         | K8s Deployment（含 kubeconfig volume mount）                                     |
| [rbac.yaml](rbac.yaml)                     | **ClusterRole** + ClusterRoleBinding                                             |
| [configmap.yaml](configmap.yaml)           | 非敏感配置                                                                       |
| [secret-example.yaml](secret-example.yaml) | Secret 字段示例（含 `k8s-deployer-secrets` + `deployer-kubeconfig` 两个 Secret） |

> 关于 `entrypoint.sh` 里调用的 `./config.sh` 和 `./run.sh`：**不在本仓**，由 Dockerfile 下载 actions-runner tarball 并 `tar xzf` 到 `/home/deployer/actions-runner/` 提供（entrypoint 头部注释写了）。entrypoint 加了 preflight 检查 + kubectl 可用性校验。

## 升级 / 扩容 / 故障

见 [runners.md §3.6](../../../pipeline/generic-layer/runners.md#36-升级--扩容--故障排查)。
