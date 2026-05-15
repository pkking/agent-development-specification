# projects/template/.github/workflows/

> 项目接入流水线时要拷到自己仓的 6 个 workflow 文件。占位符 `<<...>>` 按 [`../../ONBOARDING-CHECKLIST.md`](../../ONBOARDING-CHECKLIST.md) 逐字替换。

## 6 个 .tmpl 怎么用

| 文件                                                                               | 放哪                                             | 干啥                                                                                   | 流水线位置                                                                                     |
| ---------------------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [`caller-workflow.yml.tmpl`](caller-workflow.yml.tmpl)                             | 项目**来源仓**（如 backlog）`.github/workflows/` | 监听 issue_comment 把触发词 dispatch 给 umbrella 仓                                    | [阶段 2 / 3](../../../../pipeline/architecture.md#2-阶段-2maintainer-accept)                   |
| [`pr-preview-caller.yml.tmpl`](pr-preview-caller.yml.tmpl)                         | 项目**dev 仓**`.github/workflows/`               | 监听 PR opened/synchronize/closed 把 dispatch 给 umbrella 仓的 `pr-deploy-preview.yml` | [旁支预览](../../../../pipeline/architecture.md#7-旁支人工提-pr-的预览不走需求流)              |
| [`issue-1-analyze-requirement.yml.tmpl`](issue-1-analyze-requirement.yml.tmpl)     | 项目**umbrella 仓**`.github/workflows/`          | 流程 1：需求分析（写需求 PR / user-view 回评）                                         | [§4 流程 1](../../../../pipeline/architecture.md#4-流程-1服务名需求分析--ai-写需求文档)        |
| [`issue-2-implement-and-preview.yml.tmpl`](issue-2-implement-and-preview.yml.tmpl) | 项目**umbrella 仓**                              | 流程 2：4 agent 对抗 + 起预览                                                          | [§5 流程 2](../../../../pipeline/architecture.md#5-流程-2服务名需求实现--4-agent-对抗--起预览) |
| [`issue-3-merge-and-deploy.yml.tmpl`](issue-3-merge-and-deploy.yml.tmpl)           | 项目**umbrella 仓**                              | 流程 3：白名单门禁 → merge PR → promote → cleanup                                      | [§6 流程 3](../../../../pipeline/architecture.md#6-流程-3服务名需求上线--合入--上-beta--清理)  |
| [`pr-deploy-preview.yml.tmpl`](pr-deploy-preview.yml.tmpl)                         | 项目**umbrella 仓**                              | 旁支：人工提 PR 起 / 清预览（不走需求流）                                              | [§7 旁支](../../../../pipeline/architecture.md#7-旁支人工提-pr-的预览不走需求流)               |

## 三方拓扑

```
[来源仓 caller-workflow]      [dev 仓 pr-preview-caller]
       │ dispatch                   │ dispatch
       ▼                            ▼
   [umbrella 仓 issue-1/2/3.yml]  [umbrella 仓 pr-deploy-preview.yml]
       │                            │
       ▼ runs-on: ai-dev-runner     ▼ runs-on: k8s-deployer
   跑 orchestrate.sh / 4 agent     调 deploy.py 起 / 清预览
```

## 占位符清单

按 [`../../ONBOARDING-CHECKLIST.md`](../../ONBOARDING-CHECKLIST.md) 替换，每个 .tmpl 都会用到下面一部分：

| 占位符                     | 例                                         | 在哪几个 yml 里出现             |
| -------------------------- | ------------------------------------------ | ------------------------------- |
| `<<PROJECT_NAME>>`         | `om-datacenter`                            | issue-2 / 3 / pr-deploy-preview |
| `<<PROJECT_DISPLAY_NAME>>` | `数据中台`                                 | 所有                            |
| `<<TRIGGER_PREFIX>>`       | `数据中台`                                 | issue-1 / 2 / 3、caller         |
| `<<DEPLOY_MODE>>`          | `dev-pod` / `data-pod` / `shared` / `none` | issue-2 / pr-deploy-preview     |
| `<<NAMESPACE>>`            | `ai-test`                                  | issue-2 / 3 / pr-deploy-preview |
| `<<BASE_DOMAIN>>`          | `ai.test.osinfra.cn`                       | issue-2 / pr-deploy-preview     |
| `<<MAINTAINER_WHITELIST>>` | `alice bob`                                | issue-3                         |
| `<<BACKLOG_REPO>>`         | `opensourceways/backlog`                   | issue-1 / 2                     |

## 必须的 Secret（项目 umbrella 仓 Settings → Secrets）

完整清单见 [`../../../../src/runner/ai-dev-runner/README.md` §必须的 Token / 配置](../../../../src/runner/ai-dev-runner/README.md#必须的-token--配置部署-runner-前要先准备)；流水线 yml 直接 `secrets.X` 引到的有：

| Secret                                                                                                           | 用在哪个 yml                          |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| [`BACKLOG_REPO_TOKEN`](../../../../pipeline/generic-layer/credentials-storage.md) / `CROSS_REPO_TOKEN`           | 全部                                  |
| `OPENCODE_API_KEY`（或 [`ANTHROPIC_API_KEY`](../../../../pipeline/generic-layer/credentials-storage.md)）        | issue-1 / issue-2                     |
| [`AI_TEST_KUBECONFIG`](../../../../pipeline/generic-layer/credentials-storage.md)                                | issue-2 / issue-3 / pr-deploy-preview |
| `JENKINS_API_USER` / [`JENKINS_API_TOKEN`](../../../../pipeline/generic-layer/credentials-storage.md)            | issue-3                               |
| [`LOCAL_DB_PASSWORD`](../../../../pipeline/generic-layer/credentials-storage.md)（项目专有，如 APIMagic per-PR） | issue-2 注释段（按需放开）            |

## 实例参考

om-datacenter 的实际生产版本（已填好占位符）：[`../../../om-datacenter/.github/workflows/`](../../../om-datacenter/.github/workflows/)

## 关联

- 接入自检：[`../../ONBOARDING-CHECKLIST.md`](../../ONBOARDING-CHECKLIST.md)
- 项目模板根：[`../../README.md`](../../README.md)
- 流水线全景：[`../../../../pipeline/architecture.md`](../../../../pipeline/architecture.md)
- 跨仓 forward workflow（来源仓 caller 之前的那一层）：[`../../../../teams/external-workflows/`](../../../../teams/external-workflows/)
