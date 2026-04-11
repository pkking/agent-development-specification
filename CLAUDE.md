# Agent-Development-Specification 说明

本仓库是团队使用 Claude Code 进行协作开发时的**规范体系模板集合**，定义了三层规范架构的标准文件结构、内容模板和使用说明。

---

## 依赖

依赖Prettier组件用于格式化markdown等文件, 安装指令:

```
npm install --save-dev --save-exact prettier
```

## 项目定位

这不是一个可运行的应用，而是一套**规范文档模板库**。目标是：

- 为团队提供可直接复用的 Claude Code 配置模板
- 定义三层规范体系的结构和演进流程
- 提供 Commands、Hooks、CLAUDE.md 的编写示例

---

## 三层规范体系

```
Layer 3 · 个人层   ~/.claude/CLAUDE.md + ~/.claude/commands/
                       ↑ 优先级最高，可覆盖下层
Layer 2 · 项目层   <project>/CLAUDE.md + .claude/commands/ + .claude/settings.json
                       ↑
Layer 1 · 团队层   team-standards 仓库 / CLAUDE.md + docs/standards/
```

---

## 目录结构

```
README.md                               # 体系总览，三层架构说明，快速上手
specification-example/
├── team/                               # Layer 1：团队级规范模板
│   ├── CLAUDE.md                       # 团队 Claude 入口：核心工作原则 + 行为约束
│   └── docs/standards/
│       ├── architecture.md             # 架构原则与 ADR 机制
│       ├── coding/
│       │   ├── base.md                 # 通用编码规范（语言无关）
│       │   ├── go.md                   # Go 专项规范
│       │   ├── python.md               # Python 专项规范
│       │   └── typescript.md           # TypeScript 专项规范
│       ├── docs-writing.md             # 文档写作规范
│       ├── security.md                 # 安全开发规范
│       ├── testing.md                  # 测试策略与规范
│       ├── git-workflow.md             # Git 分支、Commit、PR 流程
│       ├── api-design.md              # API 设计（REST/gRPC）
│       ├── database.md                # 数据库设计与迁移
│       ├── observability.md           # 日志、指标、链路追踪
│       └── release.md                 # 发布流程与回滚
├── project/                            # Layer 2：项目级规范模板
│   ├── CLAUDE.md                       # 项目 Claude 入口模板（含占位符，需按项目填写）
│   ├── .claude/
│   │   ├── README.md                   # Commands + Hooks 完整使用说明
│   │   ├── settings.json               # Hooks 配置示例（lint、防护、通知）
│   │   └── commands/
│   │       ├── README.md               # 命令列表索引
│   │       ├── review.md               # /review：全面代码 Review
│   │       ├── test.md                 # /test：生成单元测试
│   │       ├── migrate.md              # /migrate：创建数据库迁移
│   │       ├── debug.md                # /debug：系统性排查 Bug
│   │       ├── release-note.md         # /release-note：生成发布说明
│   │       ├── adr.md                  # /adr：创建架构决策记录
│   │       ├── security-check.md       # /security-check：安全专项检查
│   │       ├── refactor.md             # /refactor：安全重构
│   │       └── api-design.md           # /api-design：设计 API 接口
│   └── docs/standards/
│       ├── build.md                    # 构建规范（每个项目必须填写）
│       └── architecture.md             # 项目架构说明（可选，覆盖团队层）
└── personal/
    └── CLAUDE.md                       # Layer 3：个人配置模板
spec/                                   # 占位目录（待建设）
```

---

## 核心设计原则

1. **三层优先级**：个人层 > 项目层 > 团队层，下层是基础，上层可覆盖或扩展
2. **规范即代码**：所有规范文件随 Git 仓库版本管理，通过 PR Review 演进
3. **最小改动**：Claude 只做被明确要求的修改，不擅自重构周边代码
4. **可验证交付**：每次修改后主动运行相关测试或说明验证方式

---

## 关键文件说明

### Hooks（.claude/settings.json）

项目模板已配置三类 Hook：

| Hook           | 事件                       | 作用                              |
| -------------- | -------------------------- | --------------------------------- |
| 阻止 push main | `PreToolUse` (Bash)        | 防止直接推送保护分支，exit 2 阻断 |
| 自动 lint      | `PostToolUse` (Edit/Write) | 文件改动后自动检查，反馈给 Claude |
| 完成通知       | `Stop`                     | 长任务完成后 macOS 桌面通知       |

Hook 退出码：`0` 继续、`2`（仅 PreToolUse）阻止工具调用、其他非零记录错误但继续。

### Commands（.claude/commands/）

- 文件名即命令名：`review.md` → `/review`
- 子目录形成命名空间：`db/migrate.md` → `/db:migrate`
- `$ARGUMENTS` 会被替换为用户命令后输入的文本
- 第一行 `#` 标题显示在 `/` 命令菜单中

### 搜索待填写内容

```bash
grep -r "\[团队填写\]\|\[填写\]\|\[占位符\]" specification-example/
```

---

## 演进流程

```
个人在 ~/.claude/commands/ 验证新命令
    ↓ 效果好，有通用价值
提 PR 到项目 .claude/commands/
    ↓ 多个项目都需要
提 PR 到 team-standards/.claude/commands/
    ↓ 脚手架更新后自动注入新项目
```

---

## 使用方式

- **新成员**：参考 `specification-example/personal/CLAUDE.md` 初始化 `~/.claude/CLAUDE.md`
- **新项目**：复制 `specification-example/project/` 目录结构，填写所有 `[填写]` 占位符
- **团队规范**：`specification-example/team/docs/standards/` 中的文档可直接 clone 到 `~/team-standards/`
