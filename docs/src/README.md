# 公共代码（src/）

> 流水线自身使用的所有公共代码。被 [`../pipeline/`](../pipeline/) 引用，被 [`../projects/`](../projects/) 中各项目共享。

## 子目录

| 目录 | 内容 | 关联 |
|---|---|---|
| [`runner/`](runner/) | 2 类 self-hosted runner 的 Dockerfile + 启动脚本 + K8s 部署 | [`../pipeline/generic-layer/runners.md`](../pipeline/generic-layer/runners.md) |
| [`orchestrator/`](orchestrator/) | 多 agent 对抗编排脚本 `orchestrate.sh` | [`../pipeline/generic-layer/orchestrator.md`](../pipeline/generic-layer/orchestrator.md) |
| [`deployer/`](deployer/) | K8s 预览部署器 `deploy.py` + 模板 + 注册表 | [`../pipeline/generic-layer/deployer.md`](../pipeline/generic-layer/deployer.md) |
| [`gates/`](gates/) | 4 项确定性门禁 + 自动修复 | [`../pipeline/generic-layer/gates.md`](../pipeline/generic-layer/gates.md) |
| [`tests/`](tests/) | 分层测试入口 `run_layered.sh` | [`../pipeline/generic-layer/tests.md`](../pipeline/generic-layer/tests.md) |
| [`lib/`](lib/) | 公共函数库（github-api / gitcode-api / k8s-client） | 被 orchestrator / deployer / gates 引用 |

## 设计原则

1. **通用层**：不写死任何项目特定的逻辑（如子仓数、目录名、镜像名）。项目特定逻辑由项目仓的 CLAUDE.md / `.preview/service.yaml` 提供。
2. **可替换**：每个组件有清晰输入输出契约，允许项目层覆盖或替换。
3. **失败可调试**：stdout 全部进 phase log；失败时给可执行的本地复现命令。
