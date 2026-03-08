# Claude 开发规范体系

本仓库定义了团队使用Claude Code进行协作开发时的**三层规范体系**，确保AI辅助开发在团队、项目、个人三个维度上保持团队要求一致且个人风格保留。

---

## 这个仓库是做什么的

本仓库有两个核心用途：

1. **`spec/` — 插件读取的实际规范内容**（团队级规范 + 项目模板，由 Claude Code 插件自动注入）
2. **`specification-example/` — 参考示例**（展示各层规范文件应该长什么样，供人工参考和学习）

> 简单说：`spec/` 是"用的"，`specification-example/` 是"看的"。

---

## 三层架构总览

```
Layer 3 · 个人层        ~/.claude/CLAUDE.md
                         ~/.claude/commands/          ← 个人专属命令（本机生效）
                            ↓ 覆盖 / 扩展
Layer 2 · 项目层        <project>/CLAUDE.md
                         <project>/docs/standards/    ← 项目特有规范
                         <project>/.claude/commands/  ← 项目共享命令（提交仓库）
                         <project>/.claude/settings.json ← 项目 Hooks 配置
                            ↓ 覆盖 / 扩展
Layer 1 · 团队层        本仓库 spec/teams/
                         CLAUDE.md
                         docs/standards/              ← 团队规范文档
                         .claude/commands/            ← 团队通用命令
```

**优先级：个人层 > 项目层 > 团队层**（下层是基础，上层可覆盖或扩展）

---

## 目录结构

```
README.md                                        # 本文件，体系总览
│
├── spec/                                        # ★ 插件读取的实际规范内容
│   ├── teams/                                   # Layer 1：团队级规范（对所有项目生效）
│   │   ├── CLAUDE.md                            # 团队 Claude 入口 + 工作约束
│   │   └── docs/standards/                      # 团队规范文档
│   │       ├── architecture.md
│   │       ├── coding/base.md
│   │       ├── coding/<lang>.md
│   │       ├── testing.md
│   │       ├── security.md
│   │       ├── docs-writing.md
│   │       ├── git-workflow.md                  # Git 分支、Commit、PR 流程
│   │       ├── api-design.md                    # API 设计（REST/gRPC）
│   │       ├── database.md                      # 数据库设计与迁移
│   │       ├── observability.md                 # 日志、指标、链路追踪
│   │       └── release.md                       # 发布流程与回滚
│   └── project-templates/                       # Layer 2：项目初始化模板
│       └── golang/                              # Go 项目模板
│           ├── CLAUDE.md
│           ├── .claude/
│           │   ├── settings.json
│           │   └── commands/
│           └── docs/standards/build.md
│
└── specification-example/                       # 参考示例（学习用，非插件读取）
    ├── team/                                    # 团队层示例
    ├── project/                                 # 项目层示例（含完整 Commands + Hooks 说明）
    └── personal/                                # 个人层示例
        └── CLAUDE.md
```

---

## 插件工作机制

Claude Code 插件会在以下时机自动将 `spec/` 中的规范注入到对话上下文：

- **新项目初始化**：从 `spec/project-templates/<lang>/` 复制模板到项目根目录
- **对话开始时**：将 `spec/teams/CLAUDE.md` 及规范文档作为背景上下文加载
- **项目层覆盖**：项目自身的 `CLAUDE.md` 和 `.claude/` 配置优先级高于团队层

团队层规范的修改（PR 合并到本仓库）会自动被所有项目的下次对话使用，无需各项目手动同步。

---

## 团队共同维护的内容

三层体系不是"定义完就结束"的文档，而是需要团队持续共建的活文档。以下是各类内容的维护责任和协作方式。

### 规范文档（docs/standards/）

团队所有成员都应参与规范的演进，而非只有技术负责人才能修改。

| 文件                             <br/>                    | 说明                    | 维护方式                |
|---------------------------------------------------------|-----------------------|---------------------|
| `spec/teams/docs/standards/architecture.md`             | 架构原则与 ADR 机制          | 架构师主导，PR Review 决策  |
| `spec/teams/docs/standards/coding/base.md`              | 通用编码规范（语言无关）          | 全员提 PR，技术负责人 Review |
| `spec/teams/docs/standards/coding/go.md`                | Go 专项规范               | Go 开发者维护            |
| `spec/teams/docs/standards/coding/python.md`            | Python 专项规范           | Python 开发者维护        |
| `spec/teams/docs/standards/coding/typescript.md`        | TypeScript 专项规范       | 前端/TS 开发者维护         |
| `spec/teams/docs/standards/testing.md`                  | 测试策略与规范               | 全员提 PR              |
| `spec/teams/docs/standards/security.md`                 | 安全开发规范                | 安全负责人 + 全员提 PR      |
| `spec/teams/docs/standards/docs-writing.md`             | 文档写作规范                | 全员提 PR              |
| `spec/teams/docs/standards/git-workflow.md`             | Git 工作流规范（分支、Commit、PR） | 全员提 PR，技术负责人 Review |
| `spec/teams/docs/standards/api-design.md`               | API 设计规范（REST/gRPC）     | 架构师主导，全员提 PR        |
| `spec/teams/docs/standards/database.md`                 | 数据库设计与迁移规范             | DBA + 后端开发者维护       |
| `spec/teams/docs/standards/observability.md`            | 日志与可观测性规范              | SRE / 后端开发者维护       |
| `spec/teams/docs/standards/release.md`                  | 发布流程与回滚规范              | 技术负责人主导，全员提 PR      |
| `spec/project-templates/<lang>/docs/standards/build.md` | 构建规范模板，**项目初始化后必须填写** | 项目负责人负责，开发者补充       |

> **参考示例见 `specification-example/`，搜索 `[团队填写]` 找到所有待集体决策的空白。**

### 自定义命令（.claude/commands/）

Commands 是效率工具，鼓励全员贡献。好的个人命令应提升为项目或团队命令。

| 层级  | 位置                                                | 维护者    | 当前内容                                  |
|-----|---------------------------------------------------|--------|---------------------------------------|
| 团队层 | `spec/project-templates/<lang>/.claude/commands/` | 技术负责人  | 新项目初始化时注入                             |
| 项目层 | `<project>/.claude/commands/`                     | 项目团队全员 | 9 个示例命令（见下方列表，按需扩展） |
| 个人层 | `~/.claude/commands/`                             | 个人自维护  | 不提交仓库，个人沉淀                            |

**协作流程：**

```
个人在 ~/.claude/commands/ 验证新命令
    ↓ 效果好，有通用价值
提 PR 到项目 .claude/commands/
    ↓ 多个项目都需要
提 PR 到本仓库 spec/project-templates/<lang>/.claude/commands/
    ↓ 新项目初始化时自动包含
```

**已提供的示例命令：**

| 命令 | 用途 |
| --- | --- |
| `/review` | 对当前改动做全面代码 Review |
| `/test` | 为指定文件或功能生成单元测试 |
| `/migrate` | 创建数据库迁移文件 |
| `/debug` | 系统性排查 Bug（假设 → 验证 → 修复） |
| `/release-note` | 从 git log 生成发布说明 |
| `/adr` | 创建架构决策记录（ADR） |
| `/security-check` | 对当前改动做安全专项检查 |
| `/refactor` | 指导安全重构（保持行为不变） |
| `/api-design` | 设计 API 接口（遵循 API 规范） |

**欢迎继续贡献新命令：**

- `/onboard`：新成员项目快速上手引导
- 更多领域命令（按团队实际需求沉淀）

### Hooks 配置（.claude/settings.json）

Hooks 是 Claude Code 的自动化防护层，应随项目成熟度逐步加强。

| 层级        | 位置                                | 维护者   | 提交仓库             |
|-----------|-----------------------------------|-------|------------------|
| 项目层（团队共享） | `<project>/.claude/settings.json` | 项目负责人 | **是**（质量门禁对全员生效） |
| 个人层（个人偏好） | `~/.claude/settings.json`         | 个人    | 否                |

**当前项目模板已包含的 Hooks（`project/.claude/settings.json`）：**

| Hook         | 事件                         | 作用                     |
|--------------|----------------------------|------------------------|
| 阻止 push main | `PreToolUse` (Bash)        | 防止 Claude 直接推送到保护分支    |
| 自动 lint      | `PostToolUse` (Edit/Write) | 文件修改后自动检查，结果反馈给 Claude |
| 完成通知         | `Stop`                     | 长任务完成后发送桌面通知           |

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

### 新成员 Day 1 操作（必做）

**第一步：配置个人 Claude 设置**

```bash
# 参考个人层模板，配置你的工作风格偏好
cp specification-example/personal/CLAUDE.md ~/.claude/CLAUDE.md
# 打开编辑，填写个人偏好（回复语言、操作确认习惯等）
```

**第二步：了解当前项目的规范**

进入任何项目后：

- 读项目根目录的 `CLAUDE.md`——这是该项目的 Claude 规范入口
- 读 `docs/standards/build.md`——本地开发环境启动方式、常用命令
- 在 Claude Code 中输入 `/` 查看项目提供的自定义命令列表

**第三步：理解团队规范（按需）**

团队级规范存放在本仓库 `spec/teams/docs/standards/`，涵盖：

- 编码规范（通用 + Go / Python / TypeScript 专项）
- 测试策略
- 安全开发要求
- 文档写作规范
- Git 工作流（分支、Commit、PR 流程）
- API 设计（REST/gRPC）
- 数据库设计与迁移
- 日志与可观测性
- 发布流程与回滚

插件会自动将这些规范注入 Claude 上下文，通常无需手动阅读全部，但遇到规范相关问题时可直接查阅。

---

### 新项目初始化

**方式一：使用插件（推荐）**

插件会自动从 `spec/project-templates/<lang>/` 复制模板到新项目，包含：

- 项目根目录 `CLAUDE.md`（含团队规范引用）
- `.claude/settings.json`（Hooks：防护 + 自动 lint + 完成通知）
- `.claude/commands/`（9 个基础命令：`/review` `/test` `/migrate` `/debug` `/release-note` `/adr` `/security-check` `/refactor` `/api-design`）
- `docs/standards/build.md`（待填写的构建规范模板）

**方式二：手动复制**

```bash
# 以 Go 项目为例
cp -r spec/project-templates/golang/. <your-project>/

# 然后填写项目信息
# 1. 编辑 CLAUDE.md，替换所有 [填写] 占位符
# 2. 填写 docs/standards/build.md（本地启动方式、必填环境变量等）
```

**初始化后必做：**

```bash
# 找到所有待填写的占位符
grep -r "\[填写\]" <your-project>/
```

---

### 贡献新规范或命令

```bash
# 1. 在项目 .claude/commands/ 下新建并验证
vim .claude/commands/<command-name>.md

# 2. 在 Claude Code 中立即可用（输入 / 查看命令列表）

# 3. 效果好、有通用价值 → 提 PR 到本仓库
git add spec/project-templates/<lang>/.claude/commands/<command-name>.md
git commit -m "feat: add /<command-name> command for <用途>"
```

---

## 各层职责边界

| 层级   | 位置                  | 管理者              | 规范文档               | Commands       | Hooks              |
| ------ | --------------------- | ------------------- | ---------------------- | -------------- | ------------------ |
| 团队层 | 本仓库 `spec/teams/`  | 技术负责人 / 架构师 | 跨项目通用原则         | 通用工作流命令 | 不适用             |
| 项目层 | 各项目仓库 `.claude/` | 项目负责人 + 全员   | 项目特有约定、构建规则 | 项目特有命令   | 质量门禁、安全防护 |
| 个人层 | `~/.claude/`          | 个人开发者          | 工作风格、个人偏好     | 个人探索命令   | 个人习惯自动化     |

**模板来源：** 项目层的初始文件来自本仓库 `spec/project-templates/<lang>/`，由插件注入或手动复制后在各项目仓库独立维护。

---

## 文件命名约定

| 规范类型     | 文件名                            | 层级         |
| ------------ | --------------------------------- | ------------ |
| 架构规范     | `docs/standards/architecture.md`  | 团队 / 项目  |
| 编码基础     | `docs/standards/coding/base.md`   | 团队         |
| 语言规范     | `docs/standards/coding/<lang>.md` | 团队         |
| 测试规范     | `docs/standards/testing.md`       | 团队         |
| 安全规范     | `docs/standards/security.md`      | 团队         |
| 文档规范     | `docs/standards/docs-writing.md`  | 团队         |
| Git 工作流   | `docs/standards/git-workflow.md`  | 团队         |
| API 设计     | `docs/standards/api-design.md`    | 团队         |
| 数据库设计   | `docs/standards/database.md`      | 团队         |
| 可观测性     | `docs/standards/observability.md` | 团队         |
| 发布流程     | `docs/standards/release.md`       | 团队         |
| 构建规范     | `docs/standards/build.md`         | 项目（必填） |
| 自定义命令   | `.claude/commands/<name>.md`      | 项目 / 个人  |
| Hooks 配置   | `.claude/settings.json`           | 项目 / 个人  |

---

## 演进流程

所有内容（规范、命令、Hooks）遵循同一条演进路径：

```
个人发现痛点或好的实践
    ↓
在个人层验证（~/.claude/commands/ 或本地实验）
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

编辑 `spec/teams/docs/standards/` 下对应文件，提 PR，技术负责人 Review 后合并。
合并后插件会在下次对话中自动使用新规范，**无需通知各项目**。

### 新增/修改项目模板

编辑 `spec/project-templates/<lang>/` 下文件，提 PR。
已存在项目不受影响（模板只在初始化时使用），新项目会自动使用最新模板。

### 新增语言模板

```bash
# 以 Python 为例
cp -r spec/project-templates/golang spec/project-templates/python
# 修改其中的语言相关内容（CLAUDE.md、build.md、commands）
git add spec/project-templates/python
git commit -m "feat: add python project template"
```

### 需要集体决策的位置

```bash
# 搜索所有待团队填写的空白
grep -r "\[团队填写\]" spec/
```
