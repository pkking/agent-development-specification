# Generic Layer — Runners

> 通用流水线的两类 self-hosted runner — 这一份是 runner 的**单文档完整入口**。读完能搞懂：怎么部署、装了什么、怎么跑起来、怎么升级 / 扩容 / 排错。
> 代码与镜像全在 [`../../src/runner/`](../../src/runner/)。

## 1. 两类 runner 总览

| Runner | 跑什么 | runs-on 标签 | 副本数（参考） | 代码 |
|---|---|---|---|---|
| `ai-dev-runner` | 流程 1 / 2 / 3 主体（4 agent 对抗 / orchestrate.sh / gates / tester） | `[self-hosted, ai-dev-runner]` | 3 | [`../../src/runner/ai-dev-runner/`](../../src/runner/ai-dev-runner/) |
| `k8s-deployer` | 起 / 清理预览部署（PR preview / 流程 3 promote / `deploy.py`） | `[self-hosted, k8s-deployer]` | 2 | [`../../src/runner/k8s-deployer/`](../../src/runner/k8s-deployer/) |

两者**镜像不同、Dockerfile 不同、注入的 RBAC 权限不同**。下面分两段讲。

---

## 2. ai-dev-runner

### 2.1 部署方式（架构）

K8s `Deployment` + `ServiceAccount` + `RBAC` + `ConfigMap` + `Secret`。**镜像由本仓 Dockerfile 构建**，不依赖第三方 runner controller（不用 actions-runner-controller / 不用 Helm chart）。

文件清单：

| 文件 | 作用 |
|---|---|
| [`../../src/runner/ai-dev-runner/Dockerfile`](../../src/runner/ai-dev-runner/Dockerfile) | 镜像定义（组件清单见 §2.2） |
| [`../../src/runner/ai-dev-runner/entrypoint.sh`](../../src/runner/ai-dev-runner/entrypoint.sh) | 容器入口：用 [`GH_RUNNER_TOKEN`](credentials-storage.md) 向 GitHub 注册 → 跑 `run.sh` 监听 job |
| [`../../src/runner/ai-dev-runner/start-runner.sh`](../../src/runner/ai-dev-runner/start-runner.sh) | 本地 `docker run` 调试用（不是生产部署路径） |
| [`../../src/runner/ai-dev-runner/build-and-push.sh`](../../src/runner/ai-dev-runner/build-and-push.sh) | 多架构镜像构建 + 推到 registry |
| [`../../src/runner/ai-dev-runner/deployment.yaml`](../../src/runner/ai-dev-runner/deployment.yaml) | K8s Deployment（envFrom / volumeMounts / resources） |
| [`../../src/runner/ai-dev-runner/rbac.yaml`](../../src/runner/ai-dev-runner/rbac.yaml) | ServiceAccount + Role + RoleBinding（最小权限）|
| [`../../src/runner/ai-dev-runner/configmap.yaml`](../../src/runner/ai-dev-runner/configmap.yaml) | 非敏感配置 |

### 2.2 镜像组件清单

完整定义见 [Dockerfile](../../src/runner/ai-dev-runner/Dockerfile)。

| 类目 | 组件 | 装它干啥 |
|---|---|---|
| 基础镜像 | `ubuntu:24.04` | 干净底座 |
| 系统包 | `ca-certificates curl wget git jq unzip xz-utils gnupg lsb-release sudo iproute2` | 通用工具 |
| 构建链 | `build-essential` | 编原生扩展 |
| Python | `python3 python3-pip python3-venv` | agent 调脚本、`fetch-issue` action、`deploy.py` |
| Node | `nodejs npm` | dev/tester agent 跑 `vitest` / `playwright`；npm 全局装 Claude CLI |
| Java | `openjdk-17-jre-headless maven` | APIMagic 相关构建 |
| K8s 工具 | `kubectl` + `helm` | tester agent 用 `kubectl exec` 验预览 pod；deploy 用 |
| GitHub 工具 | `gh` CLI | 流程里所有 issue / PR 操作 |
| LLM CLI | `@anthropic-ai/claude-code`（spec 推荐）/ `opencode`（om-datacenter 实际用）| 4 agent 跑 prompt |
| GitHub Actions Runner | `actions/runner` v2.317.0，落在 `/home/runner/actions-runner/` | 接 GitHub 派单 |
| 用户 | `runner`（非 root，带 NOPASSWD sudo） | 跑 job 的身份；`$HOME=/home/runner` |

### 2.3 部署步骤（团队 SRE 一次性跑一遍）

```
# 1. 构建镜像
cd src/runner/ai-dev-runner
REGISTRY=<your-registry>/<your-team> ./build-and-push.sh
    → 推出 <registry>/<team>/ai-dev-runner:<timestamp> + :latest

# 2. 拿 GitHub registration token（Org/Repo Settings → Actions → Runners → New self-hosted runner）

# 3. 准备命名空间和 Secret（手工，不入仓）
kubectl create ns ci-runners
kubectl -n ci-runners create secret generic ai-dev-runner-secrets \
    --from-literal=GH_RUNNER_TOKEN=<...> \
    --from-literal=OPENCODE_API_KEY=<...> \
    --from-literal=BACKLOG_REPO_TOKEN=<...> \
    --from-literal=CROSS_REPO_TOKEN=<...> \
    --from-literal=AI_TEST_KUBECONFIG=<...> \
    --from-literal=LOCAL_DB_PASSWORD=<...>

# 4. 应用 K8s 资源（顺序：RBAC → ConfigMap → Deployment）
kubectl apply -f src/runner/ai-dev-runner/rbac.yaml
kubectl apply -f src/runner/ai-dev-runner/configmap.yaml
kubectl apply -f src/runner/ai-dev-runner/deployment.yaml

# 5. 验证
kubectl -n ci-runners get pods -l app=ai-dev-runner    # 应该 N 个 Running
# 到 Org/Repo Settings → Actions → Runners 看 N 个 online runner，label 含 self-hosted, ai-dev-runner
```

### 2.4 标签

- `self-hosted, ai-dev-runner` — 标准
- 可选追加：`gpu` 给本地化大模型推理用（非默认部署不开）

### 2.5 注入的凭据

通过 `envFrom: secretRef` 一次性注入到容器 env，本目录 [`configmap.yaml`](../../src/runner/ai-dev-runner/configmap.yaml) 只放非敏感的：

| 来源 | 字段 |
|---|---|
| ConfigMap `ai-dev-runner-config` | `GH_OWNER` / `GH_REPO` / `ANTHROPIC_BASE_URL` / `ANTHROPIC_MODEL` |
| Secret `ai-dev-runner-secrets` | `GH_RUNNER_TOKEN` / [`ANTHROPIC_API_KEY`](credentials-storage.md) / `OPENCODE_API_KEY` / `BACKLOG_REPO_TOKEN` / `CROSS_REPO_TOKEN` / `AI_TEST_KUBECONFIG` / `LOCAL_DB_PASSWORD` |

凭据存储分档规则：[`credentials-storage.md`](credentials-storage.md)。

### 2.6 资源 / 挂载

参考 [`deployment.yaml`](../../src/runner/ai-dev-runner/deployment.yaml)：

| 项 | 值 |
|---|---|
| requests | `cpu=500m memory=1Gi` |
| limits | `cpu=4000m memory=8Gi` |
| `/var/run/docker.sock`（hostPath） | 让 runner 容器调宿主机 Docker（如要 build 子镜像） |
| `/workspaces`（PVC） | 流程 2 的 per-issue 工作区（`$WORKSPACE_DIR`），跨 job 持久 |

### 2.7 部署 vs 流水线时序

```
[团队 SRE 一次性做] 部署 ai-dev-runner 到 K8s
       ↓ (runner pod 持续 online，等单)
[人] 在 backlog 提 issue → /accepts → 评 [<服务名>需求...] ← 流程触发
       ↓
GitHub Actions 把 job 派给 label 匹配的 online runner pod
       ↓
runner pod 在 $GITHUB_WORKSPACE 跑 yml 里的步骤（流程 1/2/3）
```

**runner 不是「每次 job 重新部署」** — 长驻 pod；registration token 一次性，过期由 entrypoint 自动重新 register。

### 2.8 升级 / 扩容 / 故障排查

| 场景 | 操作 |
|---|---|
| 升级镜像 | 改 Dockerfile → `./build-and-push.sh` → `kubectl set image deployment/ai-dev-runner runner=<new-tag>` |
| 扩容 | `kubectl scale deployment/ai-dev-runner --replicas=N` |
| runner 卡死 / 离线 | `kubectl delete pod -l app=ai-dev-runner -n ci-runners`（Deployment 自动重建并重新 register） |
| 凭据轮换 | 更新 Secret → `kubectl rollout restart deployment/ai-dev-runner -n ci-runners` |
| job 一直 queued 跑不起来 | 1) GitHub Settings → Actions → Runners 看 online 数；2) `kubectl describe pod` 看是否 ImagePullBackOff / 凭据缺失 |
| job 跑到 Claude CLI 报 401 | `ANTHROPIC_API_KEY` 失效，按「凭据轮换」步骤 |

---

## 3. k8s-deployer

### 3.1 角色

接收来自 ai-dev-runner 的 deploy 请求（通过 `repository_dispatch` 或在 yaml 里直接 `runs-on: [self-hosted, k8s-deployer]`），调用 [`deployer.md`](deployer.md) 的 `deploy.py` 把镜像推到目标 namespace + 起预览 Ingress / 清理预览。

**为什么单独一类 runner**：ai-dev-runner 不持有目标 namespace 的 deploy / svc / ingress create 权限（最小权限原则）；k8s-deployer 才有。两者 RBAC 边界清晰。

### 3.2 部署方式 & 文件清单

与 ai-dev-runner 同构（K8s Deployment + RBAC + ConfigMap + Secret）。文件：

- [`../../src/runner/k8s-deployer/Dockerfile`](../../src/runner/k8s-deployer/Dockerfile)
- [`../../src/runner/k8s-deployer/entrypoint.sh`](../../src/runner/k8s-deployer/entrypoint.sh)
- [`../../src/runner/k8s-deployer/start-runner.sh`](../../src/runner/k8s-deployer/start-runner.sh)
- [`../../src/runner/k8s-deployer/build-and-push.sh`](../../src/runner/k8s-deployer/build-and-push.sh)
- [`../../src/runner/k8s-deployer/deployment.yaml`](../../src/runner/k8s-deployer/deployment.yaml)
- [`../../src/runner/k8s-deployer/rbac.yaml`](../../src/runner/k8s-deployer/rbac.yaml) — **包含 ClusterRole**，权限到目标 namespace 的 Deployment / StatefulSet / Service / Ingress / PVC create-update-delete
- [`../../src/runner/k8s-deployer/configmap.yaml`](../../src/runner/k8s-deployer/configmap.yaml)

### 3.3 镜像组件清单（差异处）

| 装了 | 未装（对比 ai-dev-runner） |
|---|---|
| Ubuntu 24.04 + `curl wget git jq python3 sudo` | — |
| `kubectl` + `helm` | 没 Node / 没 Java / 没 Claude CLI / 没 build-essential |
| GitHub Actions Runner | 同 ai-dev-runner |
| 用户 `deployer`（非 root） | — |

完整见 [Dockerfile](../../src/runner/k8s-deployer/Dockerfile)。

### 3.4 部署步骤

与 ai-dev-runner 同（构建 → 注册 token → ns/Secret → apply RBAC/ConfigMap/Deployment），区别：

- Secret 字段：`GH_RUNNER_TOKEN` + 包 kubeconfig 的 `deployer-kubeconfig` Secret（按 `deployment.yaml` 的 volumes 段）
- RBAC 是 ClusterRole / ClusterRoleBinding，不是 namespaced Role

### 3.5 标签

- `self-hosted, k8s-deployer`

### 3.6 升级 / 扩容 / 故障排查

同 §2.8，把 `ai-dev-runner` 换成 `k8s-deployer`。常见问题：

| 现象 | 原因 / 处理 |
|---|---|
| `deploy.py` 报 `Forbidden: cannot create deployments` | RBAC 未应用或目标 namespace 不在 ClusterRoleBinding 范围内 |
| 预览 Ingress 起得来但访问 502 | 看 `kubectl logs <preview-pod>`；多半是镜像启动失败而 readinessProbe 未及时拉低就绪 |
| `cleanup` 删不掉 PVC | data-pod 模式默认保留 PVC 一段时间（按 service.yaml 配置），不是 bug |

---

## 4. 关联

- 编排（agent 之间怎么串）：[`orchestrator.md`](orchestrator.md)
- 部署器（k8s-deployer 跑的脚本）：[`deployer.md`](deployer.md)
- 4 项确定性门禁：[`gates.md`](gates.md)
- 测试分层编排：[`tests.md`](tests.md)
- 凭据存储：[`credentials-storage.md`](credentials-storage.md)
- 全景：[`../architecture.md`](../architecture.md)
