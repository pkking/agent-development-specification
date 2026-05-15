# tools/tag — 给一个 / 一组仓打 tag + 发 release

> 业界规范的发版工具：**annotated tag**（不是 lightweight）+ SemVer + 结构化 release notes。
> 通过 GitHub REST API 一次性搞定，**不需要本地 clone 任何仓**。
> 适合 umbrella + 多 submodule 同时发版（如 om-datacenter v1.0.0 基线），也支持单仓发版。

## 为什么有这个工具

`gh release create` 默认创建**lightweight tag**（一个指向 commit 的 ref，没有自己的 commit 消息）。
对于**正式发版**（特别是基线 / 主版本），业界规范是用 **annotated tag**：

| | lightweight tag | annotated tag |
|---|---|---|
| 自带消息 | ❌ | ✓（`git show v1.0.0` 直接看 baseline 描述） |
| 自带 tagger / 时间戳 | ❌（取 commit 的） | ✓ |
| 可被 GPG 签名 | ❌ | ✓ |
| `git describe` 优先识别 | 同 | ✓ |
| SemVer / Maven / pip 的发版习惯 | — | ✓ |

本工具默认产出 annotated tag。

## 用法

### 单仓发版

```bash
python release.py \
    --owner opensourceways \
    --repo  om-datacenter \
    --branch main \
    --tag   v1.0.0 \
    --title "v1.0.0 — 数据中台基线版本" \
    --body-file        notes/om-datacenter-v1.0.0.md \
    --tag-message-file notes/baseline-tag-message.txt
```

干跑（不真改远端）：加 `--dry-run`。

只打 tag、不创建 release（用于内部里程碑）：加 `--skip-release`。

### 多仓批量发版（推荐 umbrella 项目用）

```bash
python release.py --manifest examples/om-datacenter-v1.0.0.json
```

manifest 写法见 [`examples/om-datacenter-v1.0.0.json`](examples/om-datacenter-v1.0.0.json)。manifest 里：

- `tag` / `date` / `draft` / `prerelease` 全局参数
- `tag_message`（或 `tag_message_file`）— annotated tag 的消息
- `body_template`（或 `body_template_file`）— release notes 模板，可用 `{owner}` / `{repo}` / `{branch}` / `{sha}` / `{sha_short}` / `{role}` / `{role_label}` / `{capability}` / `{matrix}` / `{extra}` 等占位符
- `repos` — 仓清单，每个含 `owner` / `name` / `branch` / `role` / `capability` / `include_matrix` 等

工具会**先**把所有仓的当前 branch HEAD SHA 拉下来构成兼容性矩阵（`{matrix}`），**再**给每个仓发 release。

### 升级既有 lightweight tag → annotated（不动 release）

如果之前的 release 是通过 `gh release create` / GitHub UI / Release API 直接创建的（默认 lightweight），可以补打 annotated：

```bash
python release.py --owner opensourceways --repo om-datacenter --tag v1.0.0 \
    --tag-message-file notes/baseline-tag-message.txt \
    --upgrade-annotated-only
```

或者 manifest + `--upgrade-annotated-only` 一次升级所有仓的 tag。

## Token 获取

按以下优先级查 PAT：

1. `--token <pat>`
2. `GITHUB_TOKEN` env
3. `GH_TOKEN` env
4. 本地 spec 仓 `.git/config` remote URL 嵌的 PAT（开发机约定，仅本地）

PAT 需要 scope：

- 仓 `contents: write`（打 tag + 发 release）
- fine-grained PAT 还要 `metadata: read`

org-level PAT 限制：详见 [`../../docs/pipeline/generic-layer/credentials-storage.md`](../../docs/pipeline/generic-layer/credentials-storage.md)。

## 业界规范的 release notes 应该包含哪些段

模板里我们用的是这套（参考了 Kubernetes / etcd / TiDB / cri-o 等大型项目）：

| 段 | 干啥 |
|---|---|
| 🎯 Overview / 标题 + 角色定位 | 一眼看出这是什么版本、给谁用 |
| 📌 基线说明 | 这是 baseline / patch / feature / breaking？回滚到这个版本会怎样 |
| ✨ 本次包含能力 | 重点 5-10 条 — 不要复述 commit log |
| 🏗️ 兼容性矩阵 | umbrella + submodule 各自锁的 SHA；下游兼容版本 |
| 📦 关联组件 | 跨仓项目的全套清单 |
| 🔧 已知限制 | 真实承认的问题（**比写 release notes 时假装没有有用**） |
| 📚 文档 / 资源 | 给读者下一步去哪 |
| 📅 版本元信息 | 版本号 / 日期 / 类型 / 分支 / SHA / 后续策略 |

模板：[`examples/baseline-tag-message.txt`](examples/baseline-tag-message.txt) + [`examples/baseline-release-body.template.md`](examples/baseline-release-body.template.md)。

## 失败处理

- HTTP 401 / 403：PAT 没权限 — 见上「Token 获取」段，检查 scope
- HTTP 404 on PATCH refs：本地误以为 tag 存在 — 工具会先 GET 检查，再选 POST/PATCH
- HTTP 422 "already_exists" on release：release 已存在（同 tag）— 工具会先 GET 检查跳过
- 网络间歇失败：直接重跑，工具是幂等的（已存在的 tag/release 跳过；annotated tag 升级时 `force=true` 覆盖 ref）

## 与流水线的关系

本工具不是流水线的一部分，是 **SRE / release manager 手动执行**的工具。可以放在：

- 本地 shell（最常见）
- CI workflow 的 manual `workflow_dispatch` job
- backlog 流程 3「合入 + 上线」的人工触发后置步骤

更多发版策略：[`../../docs/teams/standards/release.md`](../../docs/teams/standards/release.md)。

## 关联

- 团队发布规范：[`../../docs/teams/standards/release.md`](../../docs/teams/standards/release.md)
- 团队 release notes 模板：[`../../docs/teams/templates/Release/`](../../docs/teams/templates/Release/)
- 凭据档位：[`../../docs/pipeline/generic-layer/credentials-storage.md`](../../docs/pipeline/generic-layer/credentials-storage.md)
- 流水线全景：[`../../docs/pipeline/architecture.md`](../../docs/pipeline/architecture.md)
