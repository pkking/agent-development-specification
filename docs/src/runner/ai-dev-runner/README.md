# ai-dev-runner

> Self-hosted GitHub Actions runner，标签 `[self-hosted, ai-dev-runner]`，跑在 K8s 集群里。流程 1 / 2 / 3 主体（4 agent 对抗 / orchestrate.sh / gates / tester）在这上面跑。
>
> **完整文档**：[`../../pipeline/generic-layer/runners.md`](../../pipeline/generic-layer/runners.md)（10 节，覆盖部署 / 组件 / 凭据 / 资源 / 升级 / 故障）。

## 镜像里装了什么

详见 [Dockerfile](Dockerfile)。摘要：

- Ubuntu 24.04
- 系统包：`git curl wget jq unzip xz-utils gnupg sudo`
- 构建链：`build-essential` / `python3 python3-pip python3-venv` / `nodejs npm` / `openjdk-17 + maven`
- K8s 工具：`kubectl` + `helm`
- GitHub 工具：`gh` CLI
- LLM CLI：`@anthropic-ai/claude-code`（spec 推荐）或 `opencode`（om-datacenter 实际用）
- GitHub Actions Runner：`actions/runner` v2.317.0，落在 `/home/runner/actions-runner/`
- 非 root 用户 `runner`（带 NOPASSWD sudo）

完整组件对照：[runners.md §2.2](../../pipeline/generic-layer/runners.md#22-镜像组件清单)。

## 必须的 Token / 配置（部署 runner 前要先准备）

### ConfigMap（非敏感，可入仓）— [`configmap.yaml`](configmap.yaml)

| 字段 | 必填 | 含义 | 例 |
|---|---|---|---|
| `GH_OWNER` | ✓ | runner 注册到的 GitHub Org / 个人账号 | `opensourceways` |
| `GH_REPO` | ✓ | runner 注册到的仓库（也可改 Org 级） | `om-datacenter` |
| `ANTHROPIC_BASE_URL` | 用 Claude CLI 时必填 | LLM endpoint | `https://api.anthropic.com` |
| `ANTHROPIC_MODEL` | 用 Claude CLI 时必填 | 模型 id | `claude-opus-4-7` |

### Secret（敏感，**不入仓**，手工 `kubectl create secret`）

| Secret 字段 | 必填 | 用途 | 从哪拿 |
|---|---|---|---|
| `GH_RUNNER_TOKEN` | ✓ | 向 GitHub 注册 self-hosted runner 的一次性 token | GitHub: Settings → Actions → Runners → New self-hosted runner |
| `ANTHROPIC_API_KEY` | 用 Claude CLI 时 | 4 agent 调 LLM | console.anthropic.com → API Keys |
| `OPENCODE_API_KEY` | 用 opencode 时（om-datacenter 当前用） | 同上，opencode 走它的 broker | 团队 LLM 平台 |
| `BACKLOG_REPO_TOKEN` | ✓ | 跨仓 clone backlog / push 需求 PR / merge dev 仓 PR | GitHub PAT（fine-grained：对相关仓 `Contents: rw` + `Pull requests: rw` + `Issues: rw`） |
| `CROSS_REPO_TOKEN` | 流程 2 用 | clone 各 dev 子仓 + 开 PR；与 `BACKLOG_REPO_TOKEN` 任一即可（om-datacenter yml 里写成二选一 fallback） | 同上 |
| `AI_TEST_KUBECONFIG` | 流程 2/3 调 deploy.py 时 | 起预览 / 清理预览 | 集群 admin 给你的 kubeconfig（base64 编码后存入 Secret） |
| `LOCAL_DB_PASSWORD` | 仅 APIMagic per-PR 模式 | 建 `magic_api_file_v2_pr<N>` 表 | PG admin 给的密码 |

**轮换 / 失效处理**：
- `GH_RUNNER_TOKEN` 一次性；过期由 entrypoint.sh 自动重 register（用同一份 Secret 重启 pod 就行）
- 其它 token 失效：更新 Secret → `kubectl rollout restart deployment/ai-dev-runner -n ci-runners`

完整凭据档位 / 三档存储规则：[`../../pipeline/generic-layer/credentials-storage.md`](../../pipeline/generic-layer/credentials-storage.md)。

## 为什么要挂 `/var/run/docker.sock`

deployment.yaml 里有 hostPath 挂 `/var/run/docker.sock` 到容器内。**原因**：

- ai-dev-runner 里的 job 偶尔需要 **build 子镜像**（如 dev agent 改了 Dockerfile 后要本地 build 验一下，或者一些项目 workflow 里有 `docker build` step）
- 标准做法是「Docker outside of Docker」(DooD)：容器内不装 dockerd，只装 docker CLI，挂宿主机 socket，让 build 走宿主机的 daemon
- 替代方案 1：DinD（容器内跑独立 dockerd）— 资源占用大、需要 privileged
- 替代方案 2：podman / buildah / kaniko — 不需要 socket，但当前 om-datacenter workflow 里的 `actions/cache` / `docker/build-push-action` 默认走 docker socket，换工具链改动大

**安全代价**：挂 socket = 容器内对宿主机 root 等价。所以 ai-dev-runner pod **只允许调度到 CI 专用节点池**（不和业务负载混部）。如果你的安全模型不接受这个，去掉 hostPath 挂载并切到 kaniko / buildah，但要同步改用到 docker build 的 step。

## 部署步骤

1. **建镜像**：`REGISTRY=<your-registry>/<your-team> ./build-and-push.sh`
2. **拿 runner registration token**：GitHub Settings → Actions → Runners → New self-hosted runner
3. **建 namespace + Secret**：
   ```bash
   kubectl create ns ci-runners
   kubectl -n ci-runners create secret generic ai-dev-runner-secrets \
       --from-literal=GH_RUNNER_TOKEN=<...> \
       --from-literal=ANTHROPIC_API_KEY=<...> \
       --from-literal=BACKLOG_REPO_TOKEN=<...> \
       --from-literal=CROSS_REPO_TOKEN=<...> \
       --from-literal=AI_TEST_KUBECONFIG=<base64-of-kubeconfig> \
       --from-literal=LOCAL_DB_PASSWORD=<...>
   ```
4. **apply yaml**：
   ```bash
   kubectl apply -f rbac.yaml
   kubectl apply -f configmap.yaml
   kubectl apply -f deployment.yaml
   ```
5. **验证**：`kubectl -n ci-runners get pod -l app=ai-dev-runner`；GitHub Settings → Actions → Runners 看到 N 个 online。

## 资源 / 挂载（详见 [`deployment.yaml`](deployment.yaml)）

| 项 | 值 |
|---|---|
| requests | cpu 500m / memory 1Gi |
| limits | cpu 4000m / memory 8Gi |
| `/var/run/docker.sock` | hostPath，让 runner build 子镜像（见上「为什么要挂」） |
| `/workspaces` | PVC，流程 2 的 per-issue 工作区（`$WORKSPACE_DIR`），跨 job 持久 |

## 文件清单

| 文件 | 作用 |
|---|---|
| [Dockerfile](Dockerfile) | 镜像定义 |
| [entrypoint.sh](entrypoint.sh) | 容器入口：用 `GH_RUNNER_TOKEN` 注册 → 跑 `run.sh` |
| [start-runner.sh](start-runner.sh) | 本地 `docker run` 调试用 |
| [build-and-push.sh](build-and-push.sh) | 多架构 build + push |
| [deployment.yaml](deployment.yaml) | K8s Deployment |
| [rbac.yaml](rbac.yaml) | ServiceAccount + Role + RoleBinding |
| [configmap.yaml](configmap.yaml) | 非敏感配置 |

## 升级 / 扩容 / 故障

见 [runners.md §2.8](../../pipeline/generic-layer/runners.md#28-升级--扩容--故障排查)。
