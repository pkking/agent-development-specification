# Self-Hosted GitHub Actions Runners

本目录定义了两类跑在 Kubernetes 集群里的 self-hosted GitHub Actions runner，各司其职，通过不同的 RBAC 边界隔离权限。

## 两个 Runner 一句话区别

| Runner                              | 一句话                             | 能操作 K8s 资源吗                                                             |
| ----------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------- |
| **[ai-dev-runner](ai-dev-runner/)** | 跑 4-agent 对抗、gates、tester     | 只读自身 namespace                                                            |
| **[k8s-deployer](k8s-deployer/)**   | 跑 `deploy.py` 起/清/ promote 预览 | 能 create/update/delete 目标 namespace 的 Deployments、Services、Ingresses 等 |

## 为什么是两个

ai-dev-runner 只拿到 **namespace-scoped Role**（最小权限），**拿不到** Deployments/ Services/ Ingresses 的 create-update-delete 权限。k8s-deployer 才持有 **ClusterRole**，能做这些操作。

两个 runner 跑在不同的 RBAC 边界里：ai-dev-runner 最小权限 = 即使 job 被攻破也做不了 destructive K8s 操作；k8s-deployer 虽有大权限，但**不装编译工具链、不挂 docker.sock**，攻击面远小于 ai-dev-runner。

## 目录结构

```
tools/runner/
├── README.md                    ← 你在这里
├── lib/
│   └── common.sh                # 共享函数：require_env, build_and_push, register_runner 等
├── ai-dev-runner/
│   ├── README.md
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── start-runner.sh
│   ├── build-and-push.sh
│   ├── deployment.yaml
│   ├── rbac.yaml
│   ├── configmap.yaml
│   ├── pvc.yaml
│   └── secret-example.yaml
└── k8s-deployer/
    ├── README.md
    ├── Dockerfile
    ├── entrypoint.sh
    ├── start-runner.sh
    ├── build-and-push.sh
    ├── deployment.yaml
    ├── rbac.yaml
    ├── configmap.yaml
    └── secret-example.yaml
```

## 快速上手

### 构建镜像

**手动触发（推荐）：**

通过 GitHub Actions workflow_dispatch 构建并推送镜像：

1. 打开仓库 Actions → **Build Runner Images**
2. 点击 **Run workflow**
3. 选择要构建的 runner（`both` / `ai-dev-runner` / `k8s-deployer`）
4. 填写 registry 前缀，点击运行

**本地构建：**

```bash
# ai-dev-runner
cd tools/runner/ai-dev-runner
REGISTRY=registry.example.com/team ./build-and-push.sh

# k8s-deployer
cd tools/runner/k8s-deployer
REGISTRY=registry.example.com/team ./build-and-push.sh
```

### 部署到 K8s

每个 runner 目录下的 README 有完整部署步骤。概要：

1. 创建 namespace：`kubectl create ns ci-runners`
2. 创建 Secret（token 等）
3. `kubectl apply -f rbac.yaml && kubectl apply -f configmap.yaml && kubectl apply -f deployment.yaml`
4. 验证：`kubectl -n ci-runners get pod`，GitHub Settings → Actions → Runners 看到 online

### 本地调试

```bash
cd tools/runner/ai-dev-runner
# 设置必需环境变量后
./start-runner.sh
```

## 共享脚本

`lib/common.sh` 提供以下函数，两个 runner 的 `entrypoint.sh` 和 `build-and-push.sh` 都调用它：

| 函数               | 用途                                     |
| ------------------ | ---------------------------------------- |
| `require_env`      | 校验必需环境变量已设置                   |
| `build_and_push`   | 构建并推送多架构 Docker 镜像             |
| `runner_preflight` | 检查 actions-runner tarball 是否正确解压 |
| `register_runner`  | 注册 runner + 设置 EXIT trap 清理        |

## 凭据

所有凭据通过 K8s Secret 注入，**不入仓、不写死在 YAML 里**。Runner 注册使用一次性 token；容器退出时的 runner 清理建议设置 `GH_PAT`（具有 `manage_runners` 权限的 PAT）以确保可靠清理。

## 关键差异对照

| 维度            | ai-dev-runner                                           | k8s-deployer                     |
| --------------- | ------------------------------------------------------- | -------------------------------- |
| **用途**        | 流程 1/2/3 主体（agent 对抗/o rchestrate/gates/tester） | deploy.py（起/清/ promote 预览） |
| **Base 镜像**   | ubuntu:24.04                                            | ubuntu:24.04                     |
| **编译工具链**  | Node, Java 17, Maven, build-essential, python3          | python3 only                     |
| **LLM CLI**     | Claude CLI / opencode                                   | 无                               |
| **K8s 工具**    | kubectl, helm                                           | kubectl, helm                    |
| **GitHub CLI**  | gh                                                      | 无                               |
| **RBAC**        | Role（namespace-scoped）                                | ClusterRole                      |
| **docker.sock** | 挂载（DooD，build 子镜像）                              | 不挂载                           |
| **Runner 用户** | runner                                                  | deployer                         |
| **Runner 标签** | self-hosted, ai-dev-runner                              | self-hosted, k8s-deployer        |
| **PVC**         | /workspaces（跨 job 持久化）                            | 无                               |
