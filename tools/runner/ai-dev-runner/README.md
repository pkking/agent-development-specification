# ai-dev-runner

> Self-hosted GitHub Actions runner，标签 `[self-hosted, ai-dev-runner]`，跑在 K8s 集群里。流程 1 / 2 / 3 主体（4 agent 对抗 / orchestrate.sh / gates / tester）在这上面跑。
>
> 两个 runner 的对比和共性说明见 [../README.md](../README.md)。

## 镜像里装了什么

详见 [Dockerfile](Dockerfile)。摘要：

- Ubuntu 24.04
- 系统包：`git curl wget jq unzip xz-utils gnupg sudo`
- 构建链：`build-essential` / `python3 python3-pip python3-venv` / `nodejs npm` / `openjdk-17 + maven`
- K8s 工具：`kubectl` + `helm`
- GitHub 工具：`gh` CLI
- LLM CLI：`@anthropic-ai/claude-code`（spec 推荐）或 `opencode`
- GitHub Actions Runner：`actions/runner` v2.317.0，落在 `/home/runner/actions-runner/`
- 非 root 用户 `runner`（带 NOPASSWD sudo）

## 快速开始

### 构建镜像

```bash
# 本地
REGISTRY=registry.example.com/team ./build-and-push.sh

# 或通过 GitHub Actions 手动触发（推荐）
# Actions → Build Runner Images → Run workflow → 选 ai-dev-runner
```

### 部署

```bash
kubectl create ns ci-runners

# 创建 Secret（字段说明见下）
kubectl -n ci-runners create secret generic ai-dev-runner-secrets \
    --from-literal=GH_RUNNER_TOKEN=<...> \
    --from-literal=ANTHROPIC_API_KEY=<...> \
    --from-literal=BACKLOG_REPO_TOKEN=<...> \
    --from-literal=CROSS_REPO_TOKEN=<...> \
    --from-literal=AI_TEST_KUBECONFIG=<base64-of-kubeconfig> \
    --from-literal=LOCAL_DB_PASSWORD=<...>

kubectl apply -f rbac.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml

# 验证
kubectl -n ci-runners get pod -l app=ai-dev-runner
# GitHub Settings → Actions → Runners 应看到 N 个 online
```

## 必须的 Token / 配置

### ConfigMap（非敏感，可入仓）— [`configmap.yaml`](configmap.yaml)

| 字段                 | 必填                 | 含义                                  | 例                          |
| -------------------- | -------------------- | ------------------------------------- | --------------------------- |
| `GH_OWNER`           | ✓                    | runner 注册到的 GitHub Org / 个人账号 | `opensourceways`            |
| `GH_REPO`            | ✓                    | runner 注册到的仓库                   | `om-datacenter`             |
| `ANTHROPIC_BASE_URL` | 用 Claude CLI 时必填 | LLM endpoint                          | `https://api.anthropic.com` |
| `ANTHROPIC_MODEL`    | 用 Claude CLI 时必填 | 模型 id                               | `claude-opus-4-7`           |

### Secret（敏感，**不入仓**）

| Secret 字段          | 必填                     | 用途                                             |
| -------------------- | ------------------------ | ------------------------------------------------ |
| `GH_RUNNER_TOKEN`    | ✓                        | 向 GitHub 注册 self-hosted runner 的一次性 token |
| `ANTHROPIC_API_KEY`  | 用 Claude CLI 时         | 4 agent 调 LLM                                   |
| `OPENCODE_API_KEY`   | 用 opencode 时           | opencode broker key                              |
| `BACKLOG_REPO_TOKEN` | ✓                        | 跨仓 clone backlog / push 需求 PR                |
| `CROSS_REPO_TOKEN`   | 流程 2 用                | clone dev 子仓 + 开 PR                           |
| `AI_TEST_KUBECONFIG` | 流程 2/3 调 deploy.py 时 | 起预览 / 清理预览                                |
| `LOCAL_DB_PASSWORD`  | 仅 APIMagic per-PR 模式  | 建 `magic_api_file_v2_pr<N>` 表                  |

**获取 Runner Token**：GitHub → Settings → Actions → Runners → New self-hosted runner

**轮换 / 失效处理**：

- `GH_RUNNER_TOKEN` 一次性；过期由 entrypoint.sh 自动重注册（用同一份 Secret 重启 pod 就行）
- 其它 token 失效：更新 Secret → `kubectl rollout restart deployment/ai-dev-runner -n ci-runners`

## 为什么要挂 `/var/run/docker.sock`

[deployment.yaml](deployment.yaml) 里有 hostPath 挂 `/var/run/docker.sock` 到容器内。**原因**：

- ai-dev-runner 里的 job 偶尔需要 **build 子镜像**
- 标准做法是「Docker outside of Docker」(DooD)：容器内不装 dockerd，只装 docker CLI，挂宿主机 socket

**安全代价**：挂 socket = 容器内对宿主机 root 等价。所以 ai-dev-runner pod **只允许调度到 CI 专用节点池**（`nodeSelector: node-role.kubernetes.io/ci: ""`），不和业务负载混部。如果安全模型不接受，去掉 hostPath 挂载并切到 kaniko / buildah。

## 资源 / 挂载

| 项                     | 值                                           |
| ---------------------- | -------------------------------------------- |
| requests               | cpu 500m / memory 1Gi                        |
| limits                 | cpu 4000m / memory 8Gi                       |
| `/var/run/docker.sock` | hostPath，让 runner build 子镜像             |
| `/workspaces`          | PVC，流程 2 的 per-issue 工作区，跨 job 持久 |

## 本地调试

```bash
export GH_OWNER=<org> GH_REPO=<repo> GH_RUNNER_TOKEN=<token>
./start-runner.sh
```

## 文件清单

| 文件                                       | 作用                                   |
| ------------------------------------------ | -------------------------------------- |
| [Dockerfile](Dockerfile)                   | 镜像定义                               |
| [entrypoint.sh](entrypoint.sh)             | 容器入口：注册 runner → 监听 job       |
| [start-runner.sh](start-runner.sh)         | 本地 `docker run` 调试用               |
| [build-and-push.sh](build-and-push.sh)     | 构建 + 推送镜像                        |
| [deployment.yaml](deployment.yaml)         | K8s Deployment                         |
| [rbac.yaml](rbac.yaml)                     | ServiceAccount + Role + RoleBinding    |
| [configmap.yaml](configmap.yaml)           | 非敏感配置                             |
| [pvc.yaml](pvc.yaml)                       | `/workspaces` 持久卷                   |
| [secret-example.yaml](secret-example.yaml) | Secret 字段示例（**不要 apply 这个**） |
