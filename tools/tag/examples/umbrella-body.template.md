# {tag} — {project_display_name} 基线版本（umbrella）

**🌐 {role_label}**

| 字段 | 值 |
|---|---|
| 仓库 | [`{owner}/{repo}`]({repo_url}) |
| 分支 | `{branch}` |
| 锁定 commit | [`{sha_short}`]({commit_url}) |
| 发布日期 | {date} |
| 源码 zip | [{repo}-{tag}.zip]({source_zip_url}) |
| 源码 tar.gz | [{repo}-{tag}.tar.gz]({source_tgz_url}) |

---

## 📌 基线说明

这是 **{project_display_name}** 首个正式基线发布（baseline release）。`{tag}` 是后续所有补丁 / 功能 / 重构的稳定参考点：

- 任何后续发布（v1.0.x / v1.y.0 / v2.0.0）须能从本基线**清晰追溯改动**
- 生产环境回滚 / 故障复现默认回到本基线 SHA
- 兼容性问题：先验证回到本基线可复现，再分析增量改动

## ✨ 本仓本次包含

{capability}

## 🏗️ 跨仓兼容性矩阵

本基线锁定以下各仓的精确 SHA — **跨仓升级前请回到本组合验证**：

{matrix}

每个 submodule 仓都有自己独立的 `{tag}` release，**只描述自己**。要看全貌就回到本仓。

## 🔧 已知限制

{known_limits}

## 📚 文档 / 资源

{docs_links}

## 📅 版本元信息

| 字段 | 值 |
|---|---|
| 版本号 | `{tag}`（语义化版本，主版本号首次定为 1） |
| 发布日期 | {date} |
| 基线类型 | baseline release |
| 分支 | `{branch}` |
| 锁定 SHA | `{sha}` |
| 后续策略 | 补丁递增 `v1.0.x`，向前兼容功能递增 `v1.y.0`，不兼容改动 `v2.0.0` |

---

🤖 由 [`agent-development-specification/tools/tag/release.py`](https://github.com/opensourceways/agent-development-specification/blob/main/tools/tag/release.py) 产出
