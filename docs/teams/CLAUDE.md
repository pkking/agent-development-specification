# 团队级 CLAUDE 入口 — 基础设施服务团队

> 任何项目的 Claude / AI agent 工作时，本文件作为**团队级行为约束**自动加载。
> 项目层（`../projects/<project>/CLAUDE.md`）可覆盖或扩展本文件的规则。
> 优先级：个人层（`~/.claude/CLAUDE.md`）> 项目层 > 团队层（本文件）。

## 1. 团队工作原则

| 原则 | 含义 |
|---|---|
| **以 issue 为中心** | 所有改动从 backlog issue 起，PR 必须关联 issue；issue 完整流程见 [`context/team/issue-workflow-guide.md`](context/team/issue-workflow-guide.md) |
| **文档优先** | 写代码前先写需求文档 / 架构设计，PR 必带文档变更；模板见 [`templates/`](templates/) |
| **AI 主导但人把关** | AI 写代码 / 文档 / 跑测试 / 起预览；但每个阶段必须人评论或合入触发，AI 不向生产推 |
| **规范化优先复用** | 写新代码 / 文档前先查 [`standards/`](standards/)、[`templates/`](templates/)、[`context/experience/`](context/experience/)，不重造轮子 |
| **质量门禁不可绕** | 4 项确定性门禁（敏感信息 / 设计文档 / 漏洞 / License） + N 轮 AI 对抗修复，详见 [`security-gates/`](security-gates/) 与 [`../pipeline/generic-layer/gates.md`](../pipeline/generic-layer/gates.md) |

## 2. 强制约束（不可违反）

### 2.1 敏感信息绝不入仓

详见 [`standards/security.md`](standards/security.md)。提交前必跑：

- `gitleaks detect` — 自动门禁见 [`security-gates/Gitleaks.md`](security-gates/Gitleaks.md)
- 手动 grep 检查 `password|token|api[_-]?key|secret|BEGIN .* PRIVATE KEY`
- 真实凭据按 [`../pipeline/generic-layer/credentials-storage.md`](../pipeline/generic-layer/credentials-storage.md) 三档存储（GitHub Secret / K8s Secret / Vault Inject）

### 2.2 文档与代码同步

任何代码改动必须同步：

- 改 API → 更新 [`templates/`](templates/) 中对应 OpenAPI / 接口契约文档
- 改架构 → 更新 [`templates/Architecture Design/`](templates/Architecture%20Design/) 对应章节
- 改部署 → 更新项目 `docs/deployment.md`

### 2.3 公共规范优先

写新代码 / 文档前必须先查：

- [`standards/`](standards/) — 团队规范（编码 / 测试 / API / DB / 可观测性 / 安全 / 架构 / 发布 / git 流）
- [`templates/`](templates/) — 文档模板（需求分析 / 架构设计 / 测试 / 发布 / 事故复盘）
- [`context/experience/`](context/experience/) — 已沉淀的踩坑经验与 AI 辅助经验
- [`security-gates/`](security-gates/) — 安全门禁清单（Gitleaks / SAST / UT 覆盖率）

### 2.4 触发词与流水线

用户在 backlog issue 上的评论触发词由项目层定义（见 `../projects/<project>/README.md` 的「触发词」段）。
团队层不约束具体触发词，但要求 3 个流程职责固定：

| 流程 | 入口 | 产物 |
|---|---|---|
| 流程 1 需求分析 | `[<服务名>需求分析]` | 需求 PR 到 backlog 仓 |
| 流程 2 实现 + 预览 | `[<服务名>需求实现]` | dev 仓 PR + 预览 URL |
| 流程 3 合入 + 上线 | `[<服务名>需求上线]`（白名单） | 合 PR + beta 部署 |

详细每步：[`../pipeline/architecture.md`](../pipeline/architecture.md)

## 3. 规范导航

| 我要查什么 | 看这里 |
|---|---|
| 编码风格 / 命名 | [`standards/coding.md`](standards/coding.md) |
| 提交 / 分支 / PR 规范 | [`standards/git-workflow.md`](standards/git-workflow.md) |
| API 设计 | [`standards/api-design.md`](standards/api-design.md) + [`context/team/api-security.md`](context/team/api-security.md) |
| 数据库 / 迁移 | [`standards/database.md`](standards/database.md) |
| 可观测性（日志 / 指标 / 追踪） | [`standards/observability.md`](standards/observability.md) |
| 安全（编码 / 设计 / 上线） | [`standards/security.md`](standards/security.md) + [`context/team/安全编码规范.md`](context/team/安全编码规范.md) |
| 测试（写法 / 分层 / 覆盖率） | [`standards/testing.md`](standards/testing.md) |
| 架构设计 | [`standards/architecture.md`](standards/architecture.md) |
| 发布 / 上线 | [`standards/release.md`](standards/release.md) |
| 需求 / 架构 / 测试 / 发布 / 复盘文档模板 | [`templates/`](templates/) |
| AI 辅助经验沉淀 | [`context/experience/`](context/experience/) |
| 团队级 prompt（被流水线引用） | [`prompts/`](prompts/) |

## 4. 关联

- 流水线全景：[`../pipeline/architecture.md`](../pipeline/architecture.md)
- 公共代码：[`../src/`](../src/)
- 项目接入模板：[`../projects/template/`](../projects/template/)
- 当前已接入项目：[`../projects/om-datacenter/`](../projects/om-datacenter/)
