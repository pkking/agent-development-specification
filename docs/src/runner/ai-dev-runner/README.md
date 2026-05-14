# 通用 AI 开发 runner（ai-dev-runner）

> Self-hosted GitHub Actions runner, 标签 `self-hosted, ai-dev-runner`, 跑在 K8s 集群里.

## 职责

待填(见 [`../../pipeline/generic-layer/runners.md`](../../pipeline/generic-layer/runners.md))

## 镜像内容(baked)

待填: opencode / git / node / java / maven / python / kubectl 等

## 构建与发布

```
bash build-and-push.sh
```

## K8s 部署

```
kubectl apply -f deployment.yaml
kubectl apply -f rbac.yaml
kubectl apply -f configmap.yaml
```

## 文件清单

- `Dockerfile` 镜像构建
- `entrypoint.sh` 容器入口(runner config + 注册)
- `start-runner.sh` 启动 runner 主进程
- `build-and-push.sh` 构建 + push 到 SWR
- `deployment.yaml` K8s Deployment
- `rbac.yaml` ServiceAccount + RBAC
- `configmap.yaml` runner 环境配置
