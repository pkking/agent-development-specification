# 团队级 CLAUDE 入口 — 基础设施服务团队

> 任何项目的 Claude / AI agent 工作时，本文件作为**团队级行为约束**自动加载。
> 项目层（`../projects/<project>/CLAUDE.md`）可覆盖或扩展本文件的规则。
> 优先级：个人层（`~/.claude/CLAUDE.md`）> 项目层 > 团队层（本文件）。

## 1. 团队工作原则

待填：团队的核心工作原则（如：以问题为中心、文档优先、AI 主导但人把关、规范化优先复用）。

## 2. 强制约束（不可违反）

### 2.1 敏感信息绝不入仓

详见 [`standards/security.md`](standards/security.md) 第一段。提交前自检 grep 命令清单见同文档。

### 2.2 文档与代码同步

任何代码改动必须同步更新对应文档（API 描述 / 部署文档 / 设计文档）。

### 2.3 公共规范优先

写新代码 / 文档前必须先查：
- [`standards/`](standards/) — 团队规范
- [`templates/`](templates/) — 文档模板
- [`context/experience/`](context/experience/) — 踩坑经验
- [`security-gates/`](security-gates/) — 安全门禁

## 3. 规范导航

待填：标签式快速导航到本目录下其它文档。

## 4. 关联

- 流水线全景：[`../pipeline/architecture.md`](../pipeline/architecture.md)
- 公共代码：[`../src/`](../src/)
