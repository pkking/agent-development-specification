# 编码规范

> 团队级编码规范，所有项目默认遵守；项目可在 `../../projects/<project>/docs/coding-overrides.md` 中声明项目层的差异。

## 1. 通用规则

- **命名**：变量 / 函数 / 文件用小写下划线（Python / shell）或小驼峰（JS / TS）；类名用大驼峰；常量全大写下划线
- **函数长度**：单函数 ≤ 50 行；超过拆分
- **嵌套层级**：≤ 4 层；用 early-return 抽取
- **注释**：默认不写；写就写 WHY 不写 WHAT；禁止「修了什么 bug」「给谁用的」之类的瞬时信息
- **错误处理**：边界 catch，内部不 try / 不兜底；只在系统边界（用户输入 / 外部 API）做校验
- **依赖**：禁止用未声明依赖；新引入第三方库须在 PR 描述里写明用途与替代方案

## 2. 各语言细节

| 语言 | 风格指南 |
|---|---|
| Python | PEP 8；行宽 100；类型注解必填 (mypy --strict)；`from __future__ import annotations` 起头 |
| JS / TS | ESLint airbnb 基线；TS 全显式类型；禁用 `any` |
| Go | `gofmt` + `golangci-lint run`；包名小写 |
| Shell | `bash` 不写 `sh`；`set -euo pipefail` 起头；变量必加 `"$VAR"` |
| YAML | 2 空格；key 用 kebab-case；workflow 限定 `runs-on` |

## 3. 安全编码

详见 [`../context/team/安全编码规范.md`](../context/team/安全编码规范.md)：禁止字符串拼 SQL、禁止反序列化不可信数据、禁止 shell 直接拼用户输入。

## 4. 关联

- 团队 CLAUDE.md：[`../CLAUDE.md`](../CLAUDE.md)
- 安全门禁：[`../security-gates/`](../security-gates/)
- 流水线 4 项门禁：[`../../pipeline/generic-layer/gates.md`](../../pipeline/generic-layer/gates.md)
