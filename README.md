# Claude 开发规范体系

本仓库定义了团队使用 Claude Code 进行协作开发时的**两层规范体系**，确保 AI 辅助开发在团队、项目两个维度上保持要求一致。

---

## 这个仓库是做什么的

本仓库有三个核心用途：

1. **`spec/` — 插件读取的实际规范内容**（团队级规范 + 项目模板，由 Claude Code 插件自动注入）
2. **`specification-example/` — 参考示例**（展示各层规范文件应该长什么样，供人工参考和学习）
3. **`workflow/` + `tools/` — 流水线文档与公共代码**（「Issue → 发布」端到端自动化流水线的通用方法论和工具）

> 简单说：`spec/` 是"用的"，`specification-example/` 是"看的"，`workflow/` + `tools/` 是"跑的"。

---

## 两层架构总览

```
Layer 2 · 项目层        <project>/CLAUDE.md
                         <project>/.claude/rules/         ← 项目专项规范（如 Go DDD 分层）
                         <project>/.claude/settings.json  ← 项目 Hooks 配置
                            ↑ 覆盖 / 扩展
Layer 1 · 团队层         spec/teams/                      ← 团队级规范（本仓库维护）
                         CLAUDE.md                        ← 团队行为约束
                         standards/                       ← 团队规范文档
                         prompts/                         ← 团队级 prompt
                         templates/                       ← 文档模板
                         context/                         ← 团队上下文与经验
                         security-gates/                  ← 安全门禁
```

**优先级：项目层 > 团队层**（下层是基础，上层可覆盖或扩展）

---

## 目录结构

```
README.md                                        # 本文件，体系总览
│
├── spec/                                        # ★ 插件读取的实际规范内容
│   ├── teams/                                   # Layer 1：团队级规范（对所有项目生效）
│   │   ├── CLAUDE.md                            # 团队 Claude 入口：核心工作原则 + 行为约束
│   │   ├── standards/                           # 团队规范文档
│   │   │   ├── api-design.md                    # API 设计（REST/gRPC）
│   │   │   ├── architecture.md                  # 架构原则与 ADR 机制
│   │   │   ├── coding.md                        # 通用编码规范
│   │   │   ├── database.md                      # 数据库设计与迁移
│   │   │   ├── git-workflow.md                  # Git 分支、Commit、PR 流程
│   │   │   ├── observability.md                 # 日志、指标、链路追踪
│   │   │   ├── release.md                       # 发布流程与回滚
│   │   │   ├── security.md                      # 安全开发规范
│   │   │   └── testing.md                       # 测试策略与规范
│   │   ├── prompts/                             # 团队级 prompt（design/dev/review/tester 等）
│   │   ├── templates/                           # 文档模板（需求分析/架构设计/测试/发布/事故复盘）
│   │   ├── context/                             # 团队上下文
│   │   │   ├── experience/                      # AI 辅助经验沉淀 + 踩坑记录
│   │   │   └── team/                            # 安全编码/API安全/issue工作流等团队约定
│   │   ├── security-gates/                      # 安全门禁清单（Gitleaks/SAST/UT覆盖率）
│   │   └── external-workflows/                  # 外部仓库转发 workflow
│   └── project-templates/                       # Layer 2：项目初始化模板
│       ├── common/                              # 通用项目模板（不限语言）
│       │   ├── CLAUDE.md.tmpl                   # 项目 Claude 入口（含占位符）
│       │   ├── .github/workflows/               # 6 个 caller workflow .tmpl
│       │   ├── docs/                            # 项目文档模板（架构/部署/API/测试/凭据清单）
│       │   ├── prompts/                         # 流程 prompt 模板（菜单+流程1/2/3）
│       │   ├── skills/                          # 项目 skill 模板
│       │   ├── k8s/                             # K8s 资源 yaml 模板
│       │   ├── .preview/service.yaml.tmpl       # 预览部署服务定义
│       │   ├── ONBOARDING-CHECKLIST.md          # 接入自检清单（A档2步/B档5步）
│       │   └── README.md                        # 模板使用说明
│       └── golang/                              # Go 项目专用模板
│           ├── CLAUDE.md                        # Go 项目 Claude 入口（技术栈+工作流约束）
│           ├── .claude/
│           │   ├── settings.json                # Hooks 配置
│           │   └── rules/                       # ★ Go 专项规范文件
│           │       ├── framework-api.md         # 框架库 API 参考
│           │       ├── project-layout.md        # 项目目录结构与命名
│           │       ├── ddd-layers.md            # DDD 分层架构规范
│           │       ├── tech-stack.md            # 技术栈约束
│           │       ├── api-design.md            # API 设计规范
│           │       ├── logging.md               # 日志规范
│           │       ├── error-handling.md        # 错误处理规范
│           │       ├── gorm.md                  # GORM 操作规范
│           │       ├── testing.md               # 测试规范
│           │       ├── k8s.md                   # K8s 部署规范
│           │       ├── security.md              # 安全开发规范
│           │       ├── pull-request.md          # PR 规范
│           │       └── (按需扩展)
│           └── install.sh                       # 模板安装脚本
│
├── specification-example/                       # 参考示例（学习用，非插件读取）
│   ├── team/                                    # 团队层示例
│   │   ├── CLAUDE.md                            # 团队 Claude 入口示例
│   │   └── docs/standards/                      # 团队规范文档示例
│   │       ├── architecture.md
│   │       ├── coding/
│   │       │   ├── base.md
│   │       │   ├── go.md
│   │       │   ├── python.md
│   │       │   └── typescript.md
│   │       ├── testing.md
│   │       ├── security.md
│   │       ├── docs-writing.md
│   │       ├── git-workflow.md
│   │       ├── api-design.md
│   │       ├── database.md
│   │       ├── observability.md
│   │       └── release.md
│   └── project/
│       └── om-datacenter/                       # ★ 实际项目案例（B 档，全 AI 自动开发）
│           ├── CLAUDE.md                        # 项目级 Claude 入口（真实填写）
│           ├── .github/agents/                  # 5 个 AI agent prompt
│           ├── .github/workflows/               # 4 个 caller workflow
│           ├── docs/                            # 项目文档
│           ├── prompts/                         # 项目专属 prompt
│           ├── skills/                          # 项目自定义 skill
│           ├── k8s/                             # K8s 资源
│           ├── .preview/service.yaml            # 预览部署服务定义
│           ├── ONBOARDING-CHECKLIST.md          # 接入完成确认
│           └── README.md                        # 项目说明
│
├── workflow/                                    # 流水线架构文档
│   ├── README.md                                # 流水线总览与子目录导航
│   ├── architecture.md                          # ★ 单文档完整入口（必读）
│   ├── generic-layer/                           # 通用机制
│   │   ├── agents.md                            # AI agent 定义
│   │   ├── credentials-storage.md               # 凭据存储规范
│   │   ├── deployer.md                          # 部署器说明
│   │   ├── gates.md                             # 质量门禁
│   │   ├── orchestrator.md                      # 编排器说明
│   │   ├── runners.md                           # ★ Runner 单文档入口
│   │   ├── tests.md                             # 测试说明
│   │   └── workflow-skeletons.md                # Workflow 骨架
│   ├── stage-flow/                              # 端到端阶段
│   │   ├── stage-1-issue-submit.md              # 阶段1：提 issue
│   │   ├── stage-2-acceptance.md                # 阶段2：accept 门禁
│   │   ├── stage-3-trigger-menu.md              # 阶段3：菜单触发
│   │   ├── flow-1-requirement.md                # 流程1：需求分析
│   │   ├── flow-2-implementation.md             # 流程2：实现+预览
│   │   └── flow-3-release.md                    # 流程3：合入+上线
│   ├── project-layer/                           # 项目接线方法
│   │   ├── onboarding-tier-A.md                 # A 档接入（仅 PR 预览）
│   │   ├── onboarding-tier-B.md                 # B 档接入（全 AI 自动开发）
│   │   ├── claude-md-spec.md                    # CLAUDE.md 编写规范
│   │   ├── skills-spec.md                       # Skill 编写规范
│   │   ├── preview-service-yaml-spec.md         # 预览服务定义规范
│   │   └── caller-workflow-spec.md              # Caller workflow 规范
│   ├── testing-strategy.md                      # 跨项目测试策略
│   ├── pr-comment-protocol.md                   # PR/issue 评论协议
│   └── release-process.md                       # 发布流程
│
└── tools/                                       # 流水线公共代码
    ├── README.md                                # 工具总览
    ├── runner/                                  # 2 类 self-hosted runner
    │   ├── ai-dev-runner/                       # AI 开发 runner（Dockerfile+K8s部署）
    │   └── k8s-deployer/                        # K8s 部署 runner
    ├── orchestrator/                            # 多 agent 对抗编排脚本
    ├── deployer/                                # K8s 预览部署器
    ├── gates/                                   # 4 项确定性门禁+自动修复
    ├── tests/                                   # 分层测试入口
    └── lib/                                     # 公共函数库（github-api/gitcode-api/k8s-client）
```

---

## 流水线与工具

除规范体系外，本仓库还包含基础设施服务团队共用的流水线文档和工具代码。

### workflow/ — 流水线架构

定义「Issue → 发布」端到端自动化流水线的通用方法论。**第一份且唯一必读文档是 [`workflow/architecture.md`](workflow/architecture.md)**——单文档讲清楚每一阶段谁做什么、用什么 runner、什么 prompt、产出什么、下一步是什么。

[`workflow/README.md`](workflow/README.md) 提供子目录导航。

### tools/ — 流水线公共代码

流水线自身使用的所有公共代码：runner 镜像、编排脚本、部署器、门禁检查、分层测试入口、公共函数库。被 `workflow/` 引用，供各项目共享。

[`tools/README.md`](tools/README.md) 列出各组件及关联文档。

---

## 插件工作机制

Claude Code 插件会在以下时机自动将 `spec/` 中的规范注入到对话上下文：

- **新项目初始化**：从 `spec/project-templates/<type>/` 复制模板到项目根目录
- **对话开始时**：将 `spec/teams/CLAUDE.md` 及规范文档作为背景上下文加载
- **项目层覆盖**：项目自身的 `CLAUDE.md` 和 `.claude/` 配置优先级高于团队层

团队层规范的修改（PR 合并到本仓库）会自动被所有项目的下次对话使用，无需各项目手动同步。

---

## 团队共同维护的内容

两层体系不是"定义完就结束"的文档，而是需要团队持续共建的活文档。以下是各类内容的维护责任和协作方式。

### 规范文档（teams/standards/）

团队所有成员都应参与规范的演进，而非只有技术负责人才能修改。

| 文件                                    | 说明                               | 维护方式                     |
| --------------------------------------- | ---------------------------------- | ---------------------------- |
| `spec/teams/standards/architecture.md`  | 架构原则与 ADR 机制                | 架构师主导，PR Review 决策   |
| `spec/teams/standards/coding.md`        | 通用编码规范（语言无关）           | 全员提 PR，技术负责人 Review |
| `spec/teams/standards/testing.md`       | 测试策略与规范                     | 全员提 PR                    |
| `spec/teams/standards/security.md`      | 安全开发规范                       | 安全负责人 + 全员提 PR       |
| `spec/teams/standards/git-workflow.md`  | Git 工作流规范（分支、Commit、PR） | 全员提 PR，技术负责人 Review |
| `spec/teams/standards/api-design.md`    | API 设计规范（REST/gRPC）          | 架构师主导，全员提 PR        |
| `spec/teams/standards/database.md`      | 数据库设计与迁移规范               | DBA + 后端开发者维护         |
| `spec/teams/standards/observability.md` | 日志与可观测性规范                 | SRE / 后端开发者维护         |
| `spec/teams/standards/release.md`       | 发布流程与回滚规范                 | 技术负责人主导，全员提 PR    |

> **参考示例见 `specification-example/team/docs/standards/`。**

### 上下文与经验（teams/context/）

| 目录                             | 内容                                  | 维护方式               |
| -------------------------------- | ------------------------------------- | ---------------------- |
| `spec/teams/context/experience/` | AI 辅助经验沉淀、踩坑记录             | 全员提 PR              |
| `spec/teams/context/team/`       | 安全编码/AI安全/issue工作流等团队约定 | 安全负责人 + 全员提 PR |

### Prompt 与模板（teams/prompts/ + teams/templates/）

| 目录                    | 内容                                                       | 维护方式                  |
| ----------------------- | ---------------------------------------------------------- | ------------------------- |
| `spec/teams/prompts/`   | 团队级 prompt（design/dev/review/tester 等），被流水线引用 | 技术负责人主导，全员提 PR |
| `spec/teams/templates/` | 文档模板（需求分析/架构设计/测试/发布/事故复盘）           | 全员提 PR                 |

### 安全门禁（teams/security-gates/）

| 文件                                       | 内容               | 维护方式       |
| ------------------------------------------ | ------------------ | -------------- |
| `spec/teams/security-gates/Gitleaks.md`    | 敏感信息扫描门禁   | 安全负责人维护 |
| `spec/teams/security-gates/SAST.md`        | 静态代码分析门禁   | 安全负责人维护 |
| `spec/teams/security-gates/UT-coverage.md` | 单元测试覆盖率门禁 | 全员提 PR      |

### 项目模板中的专项规范（project-templates/<type>/.claude/rules/）

语言专项规范随项目模板维护，Go 模板已包含 11 个规则文件，覆盖 DDD 分层、错误处理、API 设计、安全开发等全部关注点。详见 `spec/project-templates/golang/.claude/rules/`。

**协作流程：**

```
团队成员在项目中验证新规则
    ↓ 效果好，有通用价值
提 PR 到 spec/project-templates/<type>/.claude/rules/
    ↓ 技术负责人 Review
合并 → 新项目初始化时自动包含
```

### Hooks 配置（.claude/settings.json）

Hooks 是 Claude Code 的自动化防护层，应随项目成熟度逐步加强。

| 层级               | 位置                              | 维护者     | 提交仓库                     |
| ------------------ | --------------------------------- | ---------- | ---------------------------- |
| 项目层（团队共享） | `<project>/.claude/settings.json` | 项目负责人 | **是**（质量门禁对全员生效） |

**当前项目模板已包含的 Hooks：**

| Hook           | 事件                       | 作用                                  |
| -------------- | -------------------------- | ------------------------------------- |
| 阻止 push main | `PreToolUse` (Bash)        | 防止 Claude 直接推送到保护分支        |
| 自动 lint      | `PostToolUse` (Edit/Write) | 文件修改后自动检查，结果反馈给 Claude |
| 完成通知       | `Stop`                     | 长任务完成后发送桌面通知              |

**建议逐步补充的 Hooks：**

- 阻止删除迁移文件（`PreToolUse`）
- 修改测试文件后自动运行对应测试（`PostToolUse`）
- 检测硬编码密钥（`PreToolUse`，可集成 gitleaks）
- 关键操作写入审计日志（`PostToolUse`）

---

## 本地开发环境

本仓库使用 [Prettier](https://prettier.io/) 对 Markdown 等文件进行格式检查（通过 PostToolUse Hook 自动触发）。

**安装依赖：**

```bash
npm install
```

> 依赖已锁定在 `package.json`，执行后即可使用 `npx prettier` 进行格式化。

---

## 快速上手

### 新成员 Day 1 操作

**第一步：了解团队规范体系**

进入任何项目后：

- 读项目根目录的 `CLAUDE.md`——这是该项目的 Claude 规范入口
- 团队级规范在 `spec/teams/` 下，插件会自动注入 Claude 上下文，通常无需手动阅读全部
- 遇到规范相关问题时可直接查阅 `spec/teams/standards/` 对应文件

**第二步：理解团队上下文**

`spec/teams/context/` 提供团队约定、AI 辅助经验和踩坑记录，涵盖：

- 编码规范、安全开发要求
- 测试策略
- Git 工作流（分支、Commit、PR 流程）
- API 设计（REST/gRPC）
- 数据库设计与迁移
- 日志与可观测性
- 发布流程与回滚

---

### 新项目初始化

**方式一：使用插件（推荐）**

插件会自动从 `spec/project-templates/<type>/` 复制模板到新项目。以 Go 项目为例，包含：

- 项目根目录 `CLAUDE.md`（含团队规范引用和技术栈约束）
- `.claude/settings.json`（Hooks：防护 + 自动 lint + 完成通知）
- `.claude/rules/`（12 个 Go 专项规则文件：DDD 分层、API设计、错误处理、GORM、安全等）
- `install.sh`（模板安装脚本）

**方式二：手动复制**

```bash
# Go 项目
cp -r spec/project-templates/golang/. <your-project>/

# 通用项目（不限语言）
cp -r spec/project-templates/common/. <your-project>/

# 然后按 ONBOARDING-CHECKLIST.md 填写项目信息
```

**初始化后必做：**

```bash
# 找到所有待填写的占位符
grep -r "<<" <your-project>/
```

---

### 贡献新规范或规则

```bash
# 1. 在项目中新建规范文件或修改现有规则
vim .claude/rules/<rule-name>.md

# 2. 在 Claude Code 中验证效果

# 3. 效果好、有通用价值 → 提 PR 到本仓库
git add spec/project-templates/<type>/.claude/rules/<rule-name>.md
git commit -m "feat: add <rule-name> rule for <用途>"
```

---

## 各层职责边界

| 层级   | 位置                  | 管理者              | 规范文档                               | Rules        | Hooks              |
| ------ | --------------------- | ------------------- | -------------------------------------- | ------------ | ------------------ |
| 团队层 | 本仓库 `spec/teams/`  | 技术负责人 / 架构师 | 跨项目通用原则、prompt、模板、安全门禁 | 不适用       | 不适用             |
| 项目层 | 各项目仓库 `.claude/` | 项目负责人 + 全员   | 项目特有约定、构建规则                 | 语言专项规范 | 质量门禁、安全防护 |

**模板来源：** 项目层的初始文件来自本仓库 `spec/project-templates/<type>/`，由插件注入或手动复制后在各项目仓库独立维护。

---

## 文件命名约定

| 规范类型     | 文件名                       | 层级 |
| ------------ | ---------------------------- | ---- |
| 架构规范     | `standards/architecture.md`  | 团队 |
| 编码规范     | `standards/coding.md`        | 团队 |
| 测试规范     | `standards/testing.md`       | 团队 |
| 安全规范     | `standards/security.md`      | 团队 |
| Git 工作流   | `standards/git-workflow.md`  | 团队 |
| API 设计     | `standards/api-design.md`    | 团队 |
| 数据库设计   | `standards/database.md`      | 团队 |
| 可观测性     | `standards/observability.md` | 团队 |
| 发布流程     | `standards/release.md`       | 团队 |
| 语言专项规范 | `.claude/rules/<topic>.md`   | 项目 |
| Hooks 配置   | `.claude/settings.json`      | 项目 |

---

## 演进流程

所有内容（规范、规则、Hooks）遵循同一条演进路径：

```
团队成员在项目中验证
    ↓
效果好 → 提 PR 到所在项目层（各项目仓库）
    ↓
经项目负责人 Review 合并
    ↓
发现跨项目通用价值 → 提 PR 到本仓库 spec/
    ↓
技术负责人审批 → 合并 → 插件自动为新项目注入
```

---

## 如何维护本仓库

### 修改团队级规范

编辑 `spec/teams/standards/` 下对应文件，提 PR，技术负责人 Review 后合并。
合并后插件会在下次对话中自动使用新规范，**无需通知各项目**。

### 新增/修改项目模板

编辑 `spec/project-templates/<type>/` 下文件，提 PR。
已存在项目不受影响（模板只在初始化时使用），新项目会自动使用最新模板。

### 新增语言模板

```bash
# 以 Python 为例
cp -r spec/project-templates/golang spec/project-templates/python
# 修改其中的语言相关内容（CLAUDE.md、rules）
git add spec/project-templates/python
git commit -m "feat: add python project template"
```

### 需要集体决策的位置

```bash
# 搜索所有待团队填写的空白
grep -r "\[团队填写\]" spec/
```
