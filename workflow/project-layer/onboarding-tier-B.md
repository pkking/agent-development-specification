# 项目接入 — B 档（全 AI 自动开发）

> 完整接入，5 步完成。在 A 档基础上加 AI 多 agent 对抗实现 + 3 流程触发体系。

## 适用

- 想要「issue → 需求 → 实现 → 预览 → 上线」端到端自动化
- 愿意维护项目层 CLAUDE.md + skill + prompt
- 有 maintainer 名单做白名单

## 步骤

完成 [`onboarding-tier-A.md`](onboarding-tier-A.md) 的 2 步后加：

### 第 3 步：CLAUDE.md

在项目仓加 `CLAUDE.md`，逐字填占位符 + 项目铁规：

- 模板：[`../../projects/template/CLAUDE.md.tmpl`](../../projects/template/CLAUDE.md.tmpl)
- 规范：[`claude-md-spec.md`](claude-md-spec.md)

### 第 4 步：caller workflow + skills

- caller workflow：项目仓加 `.github/workflows/caller-workflow.yml`，dispatch issue_comment 给通用层骨架
  - 规范：[`caller-workflow-spec.md`](caller-workflow-spec.md)
- skills（可选）：`skills/` 目录加项目自定义 skill
  - 规范：[`skills-spec.md`](skills-spec.md)

### 第 5 步：项目 prompt + 文档

- 在 `projects/<project>/prompts/` 加 4 个 prompt：trigger-menu / flow-1 / flow-2 / flow-3
- 在 `projects/<project>/docs/` 加 6 个文档：architecture / coding-overrides / test-strategy / api-spec / deployment / credentials-inventory

模板：[`../../projects/template/prompts/`](../../projects/template/prompts/) + [`../../projects/template/docs/`](../../projects/template/docs/)

## 验收

按 [`../../projects/template/ONBOARDING-CHECKLIST.md`](../../projects/template/ONBOARDING-CHECKLIST.md) 验收段跑一遍。

## 实例参考

- om-datacenter：[`../../projects/om-datacenter/README.md`](../../projects/om-datacenter/README.md)

## 关联

- A 档：[`onboarding-tier-A.md`](onboarding-tier-A.md)
- 模板根：[`../../projects/template/README.md`](../../projects/template/README.md)
- 全景：[`../architecture.md`](../architecture.md)
