# 项目级 CLAUDE.md — 数据中台

> 与团队层 [`../../teams/CLAUDE.md`](../../teams/CLAUDE.md) 配套，本文件覆盖或扩展团队规范。
> 优先级：个人层 `~/.claude/CLAUDE.md` > 项目层（本文件） > 团队层。

## 1. 项目一句话

数据中台（`om-datacenter`） — 开源社区数据采集、元数据聚合与数据展示平台。

## 2. 项目档位

- 接入档位：**B 档**（全 AI 自动开发，已完整接入）
- 接入参考：[`../../pipeline/project-layer/onboarding-tier-B.md`](../../pipeline/project-layer/onboarding-tier-B.md)

## 3. 触发词

| 评论 | 流程 |
|---|---|
| `[数据中台需求]` / `[小数需求]` | 菜单 |
| `[数据中台需求分析]` / `[小数需求分析]` | 流程 1 |
| `[数据中台需求实现]` / `[小数需求实现]` | 流程 2 |
| `[数据中台需求上线]` / `[小数需求上线]` / `[小数合入上线]` | 流程 3（白名单） |

## 4. 5 个 dev 子仓

| 仓 | 用途 |
|---|---|
| `om-dataarts` | DataArts 元数据采集 |
| `om-dataarts-deployment` | om-dataarts 部署 |
| `datastat-manage-website` | 前端展示 |
| `om-deployment` | 部署 |
| `APIMagic` | API 后端 |

各子仓在主仓用 git submodule 管理。

## 5. 部署

- 部署模式：**各子仓不同**（前端走 `shared`、API 走 `dev-pod`、有状态服务走 `data-pod`） — 详见各子仓 [`.preview/service.yaml`](../../pipeline/project-layer/preview-service-yaml-spec.md)
- 预览域名基础：`ai.test.osinfra.cn`
- K8s namespace：`ai-test`

## 6. 项目铁规

- 跨子仓改动必须在 PR 描述列出受影响的所有子仓 + 同步合入策略
- 数据库 schema 改动必须先在 `om-dataarts` 仓评审通过再改 `APIMagic`
- 前端展示文案必须中英双语
- 数据采集任务的开关必须由 configmap 控制，不允许 hardcode 在代码

## 7. 覆盖团队规范的部分

- 编码风格调整：[`docs/coding-overrides.md`](docs/coding-overrides.md)
- 项目测试策略：[`docs/test-strategy.md`](docs/test-strategy.md)
- 部署细节：[`docs/deployment.md`](docs/deployment.md)
- 凭据清单：[`docs/credentials-inventory.md`](docs/credentials-inventory.md)

## 8. 关联

- 团队 CLAUDE.md：[`../../teams/CLAUDE.md`](../../teams/CLAUDE.md)
- 通用流水线全景：[`../../pipeline/architecture.md`](../../pipeline/architecture.md)
- 项目模板：[`../template/`](../template/)
