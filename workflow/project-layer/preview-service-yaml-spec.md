# 项目层 .preview/service.yaml 规范

> 项目仓 `.preview/service.yaml` 是 PR 预览部署的唯一配置入口。

## 1. 必含字段

```yaml
project: <project-name> # 必填
service: <service-name> # 必填
deploy_mode: dev-pod # dev-pod | data-pod | shared | none
image:
  registry: <registry-url>
  repo: <repo-path>
  tag: ${PR_NUMBER} # 占位符，由 deployer 替换
port: 8080
health_check:
  path: /healthz
  port: 8080
  initial_delay_seconds: 5
ingress:
  host: pr-${PR_NUMBER}.${BASE_DOMAIN}
  path: /
namespace: ${NAMESPACE} # 由 deployer 替换
```

## 2. 可选字段

| 字段              | 说明                        |
| ----------------- | --------------------------- |
| `env`             | 注入到容器的环境变量        |
| `env_from_secret` | 引用 K8s Secret             |
| `volumes`         | 挂载（仅 data-pod 模式）    |
| `resources`       | CPU / mem requests / limits |
| `test_targets`    | 覆盖默认测试命令            |
| `extra_gates`     | 加额外 gates 检查           |

## 3. 占位符

由 deploy.py 在渲染时替换：

- `${PR_NUMBER}` — PR 号
- `${BASE_DOMAIN}` — 预览域名（项目层指定）
- `${NAMESPACE}` — 目标 namespace
- `${IMAGE_FULL}` — 完整镜像名

## 4. 模板

- 模板：[`../../projects/template/.preview/service.yaml.tmpl`](../../projects/template/.preview/)

## 5. 关联

- 部署器：[`../generic-layer/deployer.md`](../generic-layer/deployer.md)
- 部署模式选择：同上
