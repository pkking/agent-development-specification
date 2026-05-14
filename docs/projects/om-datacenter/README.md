# 项目实例 — om-datacenter（数据中台）

> 第一个按 [`../template/`](../template/) 接入「Issue → 发布」端到端流水线的项目实例。
> 真实项目仓在 [`opensourceways/om-datacenter`](https://github.com/opensourceways/om-datacenter)（git submodule 套 5 个 dev 子仓）。

## 项目档位

**B 档** — 全 AI 自动开发（已完成完整接入）。

## 5 个 dev 子仓

| 仓 | 用途 |
|---|---|
| `om-dataarts` | DataArts 元数据采集 |
| `om-dataarts-deployment` | om-dataarts 部署 |
| `datastat-manage-website` | 前端展示 |
| `om-deployment` | 部署 |
| `APIMagic` | API 后端 |

## 触发词

- `[数据中台需求]` / `[小数需求]` — 菜单
- `[数据中台需求分析]` / `[小数需求分析]` — 流程 1
- `[数据中台需求实现]` / `[小数需求实现]` — 流程 2
- `[数据中台需求上线]` / `[小数需求上线]` / `[小数合入上线]` — 流程 3（白名单）

## 接入档位实际值

| 占位符 | 实际值 |
|---|---|
| `<<PROJECT_NAME>>` | `om-datacenter` |
| `<<PROJECT_DISPLAY_NAME>>` | 数据中台 |
| `<<TRIGGER_PREFIX>>` | `数据中台` / `小数`（双触发） |
| `<<DEV_REPOS>>` | `om-dataarts, om-dataarts-deployment, datastat-manage-website, om-deployment, APIMagic` |
| `<<DEPLOY_MODE>>` | 各子仓不同（见 `.preview/service.yaml`） |
| `<<BASE_DOMAIN>>` | `ai.test.osinfra.cn` |
| `<<NAMESPACE>>` | `ai-test` |
| `<<MAINTAINER_WHITELIST>>` | （白名单见项目仓 issue-3-merge-and-deploy.yml）|

## 关联

- 模板：[`../template/`](../template/)
- 通用流水线：[`../../pipeline/architecture.md`](../../pipeline/architecture.md)
- 接入 B 档详细：[`../../pipeline/project-layer/onboarding-tier-B.md`](../../pipeline/project-layer/onboarding-tier-B.md)

## 占位文档

下面各目录是按 template/ 接入的项目实例文档（待从 `opensourceways/om-datacenter` 仓拷贝改写到此）：

- `CLAUDE.md` — 项目级 CLAUDE 入口
- `docs/` — 项目文档（架构 / 编码覆盖 / 测试策略 / API / 部署 / 凭据清单）
- `skills/` — 项目自定义 skill（如 add-community）
- `prompts/` — 项目专属 prompt（trigger-menu / flow-1 / flow-2 / flow-3）
- `.github/workflows/` — caller workflow
- `.preview/service.yaml` — 预览部署服务定义
- `k8s/` — K8s 资源
