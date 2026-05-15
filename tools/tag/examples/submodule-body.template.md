# {tag} — {role_label}

| 字段        | 值                                      |
| ----------- | --------------------------------------- |
| 仓库        | [`{owner}/{repo}`]({repo_url})          |
| 分支        | `{branch}`                              |
| 锁定 commit | [`{sha_short}`]({commit_url})           |
| 发布日期    | {date}                                  |
| 源码 zip    | [{repo}-{tag}.zip]({source_zip_url})    |
| 源码 tar.gz | [{repo}-{tag}.tar.gz]({source_tgz_url}) |

---

## 📌 关于本次发布

本仓 `{tag}` 是 [`{umbrella_owner}/{umbrella_repo}`]({umbrella_repo_url}) 整体基线 `{tag}` 的一部分。
**本 release 只描述本仓自己的内容**（源码、commit、链接）。

要看跨仓兼容性矩阵 / 与其它子仓的协同 / 整体能力清单 → 见 [umbrella 仓 `{tag}` release]({umbrella_tag_url})。

## ✨ 本仓本次包含

{capability}

## 🔧 本仓已知限制

{known_limits}

## 📅 版本元信息

| 字段     | 值                                                              |
| -------- | --------------------------------------------------------------- |
| 版本号   | `{tag}`                                                         |
| 发布日期 | {date}                                                          |
| 基线类型 | baseline release                                                |
| 分支     | `{branch}`                                                      |
| 锁定 SHA | `{sha}`                                                         |
| Umbrella | [`{umbrella_owner}/{umbrella_repo}` v1.0.0]({umbrella_tag_url}) |
| 后续策略 | 补丁 `v1.0.x` / 向前兼容功能 `v1.y.0` / 不兼容 `v2.0.0`         |

---

🤖 由 [`agent-development-specification/tools/tag/release.py`](https://github.com/opensourceways/agent-development-specification/blob/main/tools/tag/release.py) 产出
