# 项目接入模板（projects/template/）

> 任何基础设施项目接入「Issue → 发布」端到端流水线的模板。
> **新项目接入流程**：`cp -r template/ <your-project>/` → 按 [`ONBOARDING-CHECKLIST.md`](ONBOARDING-CHECKLIST.md) 填占位符 → 跑自检 → 完成。

## 目录说明

| 文件 / 目录                  | 干什么                                                                                                                                                   | 必填                    |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `CLAUDE.md.tmpl`             | 项目级 Claude 入口（覆盖 / 扩展团队规范）                                                                                                                | ✓                       |
| `docs/`                      | 项目内部文档（架构 / 编码覆盖 / 测试策略 / API / 部署 / 凭据清单）                                                                                       | ✓                       |
| `skills/`                    | 项目自定义 skill（AI agent 阶段 ① design 时路由用）                                                                                                      | 可选                    |
| `prompts/`                   | 项目专属 prompt（菜单 + 流程 1/2/3 项目化定制）                                                                                                          | ✓                       |
| `.github/workflows/`         | 6 个 workflow .tmpl（caller / pr-preview-caller / issue-1/2/3 / pr-deploy-preview），用法见 [`.github/workflows/README.md`](.github/workflows/README.md) | ✓                       |
| `.github/ISSUE_TEMPLATE/`    | 项目 issue 模板                                                                                                                                          | 可选                    |
| `.preview/service.yaml.tmpl` | 预览部署服务定义（deployer 读这个起预览）                                                                                                                | ✓（B 档必填，A 档可选） |
| `k8s/`                       | K8s 资源 yaml（deployment / service / ingress / configmap）                                                                                              | ✓                       |
| `ONBOARDING-CHECKLIST.md`    | 接入自检清单（A 档 2 步 / B 档 5 步）                                                                                                                    | ✓                       |

## 占位符约定

所有 `.tmpl` 文件含以下占位符（按 [`ONBOARDING-CHECKLIST.md`](ONBOARDING-CHECKLIST.md) 替换）：

| 占位符                     | 含义                                      | 示例                              |
| -------------------------- | ----------------------------------------- | --------------------------------- |
| `<<PROJECT_NAME>>`         | 项目名（kebab-case）                      | `om-datacenter`                   |
| `<<PROJECT_DISPLAY_NAME>>` | 项目展示名                                | `数据中台`                        |
| `<<TRIGGER_PREFIX>>`       | 触发评论前缀                              | `数据中台` 或 `小数`              |
| `<<DEV_REPOS>>`            | 项目 dev 子仓列表（逗号分隔）             | `om-dataarts,APIMagic,...`        |
| `<<DEPLOY_MODE>>`          | 默认部署模式                              | `dev-pod` / `data-pod` / `shared` |
| `<<BASE_DOMAIN>>`          | 预览 URL 基础域名                         | `ai.test.osinfra.cn`              |
| `<<NAMESPACE>>`            | K8s 命名空间                              | `ai-test`                         |
| `<<MAINTAINER_WHITELIST>>` | 上线触发白名单（GitHub 用户名，空格分隔） | `<owner1> <owner2>`               |
| `<<PROJECT_OWNER>>`        | 项目 owner                                | GitHub 用户名                     |
| `<<JENKINS_JOB>>`          | promote 触发的 Jenkins job                | `<your-jenkins-job-name>`         |

## 接入档位

- **A 档（仅 PR 预览）**：见 [`../../pipeline/project-layer/onboarding-tier-A.md`](../../pipeline/project-layer/onboarding-tier-A.md) — 适合简单 web 应用
- **B 档（全 AI 自动开发）**：见 [`../../pipeline/project-layer/onboarding-tier-B.md`](../../pipeline/project-layer/onboarding-tier-B.md) — 适合需求驱动开发

## 接入完成后

按 [`ONBOARDING-CHECKLIST.md`](ONBOARDING-CHECKLIST.md) 自检；自检通过即可在项目 issue 评论 `[<TRIGGER_PREFIX>需求]` 触发完整流水线。

## 参考实例

实际接入示例：[`../om-datacenter/`](../om-datacenter/)
