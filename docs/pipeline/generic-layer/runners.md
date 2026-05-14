# Generic Layer — Runners

> 通用流水线运行环境。代码与镜像见 [`../../src/runner/`](../../src/runner/)。

## 1. 两类 runner

| Runner | 用途 | 跑哪些 workflow | 代码 |
|---|---|---|---|
| `ai-dev-runner` | AI 多 agent 对抗实现 + 起测试编排 | 流程 1 / 2 / 3 主体 | [`../../src/runner/ai-dev-runner/`](../../src/runner/ai-dev-runner/) |
| `k8s-deployer` | 把构建产物推到 K8s 预览 / beta namespace | 流程 2 起预览 + 流程 3 上 beta | [`../../src/runner/k8s-deployer/`](../../src/runner/k8s-deployer/) |

## 2. ai-dev-runner

### 2.1 容器构成

- 基础镜像：Ubuntu 24.04
- 预装：`git`、`gh`、`node`、`python3`、`docker`、`kubectl`、`helm`、`jq`、`yq`、Claude CLI
- Dockerfile：[`../../src/runner/ai-dev-runner/Dockerfile`](../../src/runner/ai-dev-runner/Dockerfile)
- 入口脚本：[`../../src/runner/ai-dev-runner/entrypoint.sh`](../../src/runner/ai-dev-runner/entrypoint.sh)
- 注册 self-hosted runner：[`../../src/runner/ai-dev-runner/start-runner.sh`](../../src/runner/ai-dev-runner/start-runner.sh)

### 2.2 标签

- `[self-hosted, ai-dev]` — 通用
- `[self-hosted, ai-dev, gpu]` — 大模型推理本地化（非默认）

### 2.3 注入的 secret（K8s 部署形态）

通过 `configMapRef` + `secretRef` 注入：

- `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` / `ANTHROPIC_MODEL`
- `GITHUB_TOKEN`（带 `workflow` scope）
- `GITCODE_TOKEN`（用于 GitCode 镜像）
- `KUBECONFIG`（用于触发部署器）
- 详见 [`credentials-storage.md`](credentials-storage.md)

### 2.4 部署

- `deployment.yaml`：[`../../src/runner/ai-dev-runner/deployment.yaml`](../../src/runner/ai-dev-runner/deployment.yaml)
- RBAC：[`../../src/runner/ai-dev-runner/rbac.yaml`](../../src/runner/ai-dev-runner/rbac.yaml)
- 镜像构建脚本：[`../../src/runner/ai-dev-runner/build-and-push.sh`](../../src/runner/ai-dev-runner/build-and-push.sh)

## 3. k8s-deployer

### 3.1 角色

接收来自 ai-dev-runner 的 deploy 请求（通过 `repository_dispatch` 或直接 RPC），调用 [`deployer.md`](deployer.md) 的 `deploy.py` 把镜像推到目标 namespace + 起预览 Ingress。

### 3.2 容器构成

- 同样 Ubuntu 24.04
- 预装：`kubectl`、`helm`、`nginx-ingress` controller 客户端
- Dockerfile：[`../../src/runner/k8s-deployer/Dockerfile`](../../src/runner/k8s-deployer/Dockerfile)

### 3.3 部署

- `deployment.yaml`：[`../../src/runner/k8s-deployer/deployment.yaml`](../../src/runner/k8s-deployer/deployment.yaml)
- RBAC：[`../../src/runner/k8s-deployer/rbac.yaml`](../../src/runner/k8s-deployer/rbac.yaml)（需具备目标 namespace 的 deploy / svc / ingress create 权限）

## 4. 关联

- 编排：[`orchestrator.md`](orchestrator.md)
- 部署器：[`deployer.md`](deployer.md)
- 凭据存储：[`credentials-storage.md`](credentials-storage.md)
- 全景：[`../architecture.md`](../architecture.md)
