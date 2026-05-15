# tools/tag — 多仓 GitHub release 工具

> 业界规范的发版工具：**annotated tag** + SemVer + 结构化 release notes，纯 GitHub REST API 一次性搞定，**不需要本地 clone 任何仓**。
> 适合 umbrella + 多 submodule 同时发版（如 om-datacenter v1.0.0 基线），也支持单仓发版。

## 设计原则

1. **每个仓的 release 只讲自己** — submodule 的 release body **只含自己仓的信息**（仓名、commit、URL、source zip 链接），加一句话「整体看 umbrella」反向链接；只有 umbrella 的 release 才汇总全局兼容性矩阵 + 跨仓清单。
2. **不复制别人的 zip 进自己的 release** — GitHub 自动生成的 source archive 已经是该仓自己的，足够了。
3. **annotated tag** — 业界规范的发版做法。`git show v1.0.0` 能直接看到完整基线说明 + tagger + 时间戳。
4. **幂等** — tag / release 已存在则 upsert；可重跑。

## 为什么用 annotated tag

`gh release create` / GitHub UI 默认创建 **lightweight tag**（只是个指向 commit 的 ref）。正式发版应该用 **annotated tag**：

| | lightweight | annotated |
|---|---|---|
| 自带 message | ❌ | ✓（`git show v1.0.0` 可见） |
| 自带 tagger / 时间戳 | ❌ | ✓ |
| 可 GPG 签名 | ❌ | ✓ |
| `git describe` 优先识别 | 同 | ✓ |
| SemVer / Maven / pip 习惯 | — | ✓ |

本工具默认产出 annotated tag。

## 用法

### 多仓 batch（标准用法）

```bash
python release.py --manifest examples/om-datacenter-v1.0.0.json
```

manifest 结构：

```jsonc
{
  "tag": "v1.0.0",
  "date": "2026-05-15",
  "tagger": { "name": "...", "email": "..." },

  // 1 个 umbrella —— release body 含全局矩阵
  "umbrella": {
    "owner": "opensourceways", "name": "om-datacenter", "branch": "main",
    "title_template":            "{tag} — 数据中台基线版本（umbrella）",
    "body_template_file":        "umbrella-body.template.md",
    "tag_message_template_file": "umbrella-tag-message.txt",
    "context": {
      "project_display_name": "数据中台",
      "role_label":           "数据中台 umbrella",
      "capability":   "- ...",      // 这一仓本次包含啥
      "known_limits": "- ...",      // 已知限制
      "docs_links":   "- ..."       // 仅 umbrella 有
    }
  },

  // N 个 submodule —— 每个 release body 只讲自己
  "submodules": [
    {
      "owner": "opensourceways", "name": "APIMagic", "branch": "main",
      "title_template":            "{tag} — APIMagic（后端 API）",
      "body_template_file":        "submodule-body.template.md",
      "tag_message_template_file": "submodule-tag-message.txt",
      "context": {
        "role_label":   "APIMagic — 后端 API（PG 数据访问层）",
        "capability":   "- 数据访问层 ...",
        "known_limits": "- ..."
      }
    },
    { "...另一个 submodule..." }
  ]
}
```

详细完整示例：[`examples/om-datacenter-v1.0.0.json`](examples/om-datacenter-v1.0.0.json)。

### 模板渲染上下文（占位符）

工具会自动注入这些占位符（按 Python str.format 替换 `{name}`）：

| 占位符 | 含义 | 在哪能用 |
|---|---|---|
| `{owner}` / `{repo}` / `{branch}` | 当前仓基本信息 | 所有 |
| `{tag}` / `{date}` | 版本号 / 日期 | 所有 |
| `{sha}` / `{sha_short}` | 当前仓本次 release 锁的 commit SHA（全 40 / 短 10）| 所有 |
| `{repo_url}` | `https://github.com/{owner}/{repo}` | 所有 |
| `{commit_url}` | `https://github.com/{owner}/{repo}/commit/{sha}` | 所有 |
| `{source_zip_url}` | `https://github.com/{owner}/{repo}/archive/refs/tags/{tag}.zip` | 所有 |
| `{source_tgz_url}` | 同上 `.tar.gz` | 所有 |
| `{matrix}` | 跨仓兼容性矩阵 markdown（自动生成）| **仅 umbrella** |
| `{umbrella_owner}` / `{umbrella_repo}` / `{umbrella_repo_url}` / `{umbrella_tag_url}` | 反向链接到 umbrella | **仅 submodule** |
| `{...任意自定义键}` | `context: {...}` 里的字段 | 所有 |

### 其他模式

| 命令 | 干啥 |
|---|---|
| `python release.py --manifest <m> --tag-only` | 只 (重) 打 annotated tag，不动 release |
| `python release.py --manifest <m> --body-only` | 只 PATCH release body，不动 tag（修文案最省事的方式） |
| `python release.py --manifest <m> --use-tag-target` | 用现有 tag 指向的 commit 作为 SHA（不取 branch HEAD）；用于「重新渲染历史版本的 body / tag-message」 |
| `python release.py --manifest <m> --dry-run` | 干跑，只打印 actions、不调 API |

### 单仓极简模式（不走 manifest）

```bash
python release.py \
    --owner opensourceways --repo my-svc --branch main --tag v1.0.0 \
    --title "v1.0.0" \
    --body-file notes/body.md \
    --tag-message-file notes/tag.txt
```

## Token 获取

按优先级查 PAT：

1. `--token <pat>`
2. `GITHUB_TOKEN` env
3. `GH_TOKEN` env
4. 本地 spec 仓 `.git/config` remote URL 嵌的 PAT（开发机约定）

PAT 需要 scope：

- 仓 `contents: write`（建 tag + release）
- fine-grained PAT 还要 `metadata: read`

## 业界规范的 release notes 应该包含哪些段

参考 Kubernetes / etcd / TiDB 等大型项目，模板里我们用的这套：

| 段 | umbrella | submodule |
|---|---|---|
| 标题 + 元信息表（仓 / 分支 / commit / zip） | ✓ | ✓ |
| 基线说明 | ✓ | ✓（指回 umbrella） |
| 本仓本次包含 | ✓ | ✓ |
| 跨仓兼容性矩阵 | ✓ | — |
| 关联组件 / 全局视图 | ✓ | — |
| 已知限制 | ✓ | ✓ |
| 文档 / 资源链接 | ✓ | —（指回 umbrella） |
| 版本元信息表 | ✓ | ✓ |

模板：[`examples/umbrella-body.template.md`](examples/umbrella-body.template.md) + [`examples/submodule-body.template.md`](examples/submodule-body.template.md) + 对应 tag-message 模板。

## 失败处理

| HTTP | 原因 | 处理 |
|---|---|---|
| 401 / 403 | PAT 没权限 | 检查 scope；fine-grained PAT 加 `contents: write` |
| 404 PATCH refs | tag 还不存在（不应该到 PATCH 分支） | 升级到最新 release.py |
| 422 release already_exists | release 重复创建 | 工具默认 PATCH 更新；如果想严格不覆盖，用 `--tag-only` |
| 网络断 | 重跑工具（幂等） | — |

## 与流水线的关系

本工具**不是流水线的一部分**，是 SRE / release manager 手动执行的工具。可以放在：

- 本地 shell（最常见）
- CI workflow 的 manual `workflow_dispatch` job
- backlog 流程 3「合入 + 上线」的人工触发后置步骤

更多发版策略：[`../../docs/teams/standards/release.md`](../../docs/teams/standards/release.md)。

## 关联

- 团队发布规范：[`../../docs/teams/standards/release.md`](../../docs/teams/standards/release.md)
- 团队 release notes 模板：[`../../docs/teams/templates/Release/`](../../docs/teams/templates/Release/)
- 凭据档位：[`../../docs/pipeline/generic-layer/credentials-storage.md`](../../docs/pipeline/generic-layer/credentials-storage.md)
- 流水线全景：[`../../docs/pipeline/architecture.md`](../../docs/pipeline/architecture.md)
