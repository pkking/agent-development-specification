# 🎯 数据中台 — {tag} 基线版本

**{role_label}**

发布时间：**{date}**
锁定 SHA：[`{sha}`](https://github.com/{owner}/{repo}/tree/{sha})（`{branch}` 分支）

---

## 📌 基线说明

这是数据中台首个**正式基线发布**（baseline release）。`{tag}` 是后续所有补丁 / 功能增强的稳定参考点：

- 任何后续发布（v1.0.1 / v1.1.0 / v2.0.0）须能从本基线**清晰追溯改动**
- 生产环境回滚 / 故障复现，**默认回到本基线 SHA**
- 兼容性问题：若上游或下游不匹配，先**验证是否回到本基线可复现**，再分析增量改动

## ✨ 本次发布包含

{capability}

{matrix}

## 📦 关联组件

完整数据中台 {tag} 由以下 5 个仓协同发布：

- 🌐 [`om-datacenter`](https://github.com/{owner}/om-datacenter) — umbrella（流水线主控）
- ⚙️ [`APIMagic`](https://github.com/{owner}/APIMagic) — 后端 API
- 🖼️ [`datastat-manage-website`](https://github.com/{owner}/datastat-manage-website) — 前端展示
- 📥 [`om-dataarts`](https://github.com/{owner}/om-dataarts) — 数据采集
- 🛠️ [`om-deployment`](https://github.com/{owner}/om-deployment) — 平台部署

跨仓兼容性见 [`om-datacenter {tag} release`](https://github.com/{owner}/om-datacenter/releases/tag/{tag}) 的兼容性矩阵。

## 🔧 已知限制

{extra}

## 📚 文档 / 资源

- 数据中台流水线全景：[`agent-development-specification/docs/pipeline/architecture.md`](https://github.com/{owner}/agent-development-specification/blob/main/docs/pipeline/architecture.md)
- 项目级 CLAUDE.md：[`agent-development-specification/docs/projects/om-datacenter/CLAUDE.md`](https://github.com/{owner}/agent-development-specification/blob/main/docs/projects/om-datacenter/CLAUDE.md)
- 团队规范：[`agent-development-specification/docs/teams/`](https://github.com/{owner}/agent-development-specification/tree/main/docs/teams)

## 📅 版本元信息

| 字段 | 值 |
|---|---|
| 版本号 | `{tag}`（语义化版本，主版本号首次定为 1） |
| 发布日期 | {date} |
| 基线类型 | baseline release（基线版本） |
| 分支 | `{branch}` |
| SHA | `{sha}` |
| 后续策略 | 补丁递增 `v1.0.x`，向前兼容功能递增 `v1.y.0`，不兼容改动 `v2.0.0` |

---

🤖 数据中台 AI 自动开发流水线产出
