# External Workflows — 跨仓 forward workflow

> 流水线开跑前的「**前置 forward**」：把**来源仓**（backlog / om-dataarts-deployment / ...）issue 上的触发评论转给项目 umbrella 仓（om-datacenter）的对应 workflow。**架构里看不见但必须存在**的那一层。

## 1. forward workflow 是什么

**问题**：流程 1/2/3 的 caller workflow 跑在项目 umbrella 仓（如 `opensourceways/om-datacenter`），但需求 issue 提在多个来源仓（backlog / 各社区项目仓）。GitHub 原生 `issue_comment` 事件不会跨仓投递，于是需要一个**桥梁 workflow** 监听来源仓的评论 + 用 `repository_dispatch` API 把事件转到 umbrella 仓。

这个桥梁就叫 **forward workflow**。每个**来源仓**都放一份。

**完整源码**：[`forward-to-datacenter.yml`](forward-to-datacenter.yml)（从 `opensourceways/backlog` 仓 `.github/workflows/forward-to-datacenter.yml` 同步而来；改动需同步两侧）。

## 2. 它干的两件事

| Job | 触发条件 | 做什么 |
|---|---|---|
| `menu` | issue 同时具备 `accepted` 标签 + 含 `[<服务名>需求]` 评论时 | 在该 issue 贴一条「可用命令菜单」（列出 `[<服务名>需求分析]` / `[<服务名>需求实现]` / `[<服务名>需求上线]` 各干啥），含 `<!-- DATACENTER_MENU -->` 锚点防重复贴 |
| `forward` | issue 评论命中 3 个触发词之一 | 通过 `repository_dispatch` POST 到 umbrella 仓 `/repos/<umbrella>/dispatches`，事件类型见下表 |

## 3. 触发词 → event_type 映射

每条触发评论的 event_type（umbrella 仓的 caller workflow 会按这些 event_type 选 issue-1/2/3 yml）：

| 触发评论 | event_type | 触发 umbrella 仓的哪个 workflow |
|---|---|---|
| `[<服务名>需求分析]` / `[<别名>需求分析]` | `backlog_analyze` | [issue-1-analyze-requirement.yml](../../projects/om-datacenter/.github/workflows/issue-1-analyze-requirement.yml) |
| `[<服务名>需求实现]` / `[<别名>需求实现]` | `backlog_implement` | [issue-2-implement-and-preview.yml](../../projects/om-datacenter/.github/workflows/issue-2-implement-and-preview.yml) |
| `[<服务名>需求上线]` / `[<别名>合入上线]` | `backlog_merge` | [issue-3-merge-and-deploy.yml](../../projects/om-datacenter/.github/workflows/issue-3-merge-and-deploy.yml) |

`client_payload` 里带：`source_repo` / `issue_number` / `issue_title` / `comment_id` / `comment_body` / `trigger_user`。

## 4. 依赖的 Secret / 配置

只需 1 个 Secret 配在**来源仓**：

| Secret | 必填 | 用途 | 怎么拿 |
|---|---|---|---|
| `DATACENTER_DISPATCH_TOKEN` | ✓ | GitHub PAT，对 umbrella 仓（`opensourceways/om-datacenter`）有 `repo` scope（fine-grained：`contents: write` + `metadata: read`）| Settings → Developer settings → Personal access tokens |

注：本 workflow 不需要 LLM token / 不需要 kubeconfig — 它就是个事件转发器，逻辑极薄。

## 5. 谁运行它

| 项 | 值 |
|---|---|
| runs-on | `ubuntu-latest`（GitHub 托管，**不用 self-hosted**）|
| timeout | 2 min / job |
| permissions | `contents: read` + `issues: write` |

## 6. 在流水线全景里的位置

```
[人] backlog 仓 issue 评 [<服务名>需求]
       ↓
backlog 仓 forward-to-datacenter.yml ← menu job → 贴菜单评论
       │
[人] 评 [<服务名>需求分析] / [实现] / [上线]
       ↓
backlog 仓 forward-to-datacenter.yml ← forward job → POST /repos/om-datacenter/dispatches
       ↓
om-datacenter 仓的 issue-1/2/3 yml 接 repository_dispatch 事件
       ↓
self-hosted ai-dev-runner 跑流程主体
```

详尽全景：[`../../pipeline/architecture.md`](../../pipeline/architecture.md) §阶段 2 / 阶段 3。

## 7. 加新来源仓接入

任何想接进本流水线的 backlog 类仓库都需要：

1. 复制本目录的 [`forward-to-datacenter.yml`](forward-to-datacenter.yml) 到新来源仓的 `.github/workflows/`
2. 在新来源仓的 Settings → Secrets 加 `DATACENTER_DISPATCH_TOKEN`
3. 如有自定义触发词（如本服务有别名），改 yml 里的 `if:` 条件 + `EVENT_TYPE` 表达式

## 8. 改动同步

本目录的 yml 是**只读 mirror**（用于 spec 仓内部可点击引用）；权威源在 `opensourceways/backlog` 仓的 `.github/workflows/forward-to-datacenter.yml`。改动顺序：

1. 先改权威源（backlog 仓），评审 + 合入
2. 再 mirror 到本目录（这一步纯文档拷贝；建议加 commit message 引用上游 PR）

## 9. 关联

- 流水线全景：[`../../pipeline/architecture.md`](../../pipeline/architecture.md)
- umbrella 仓接 dispatch 的 yml 实例：[`../../projects/om-datacenter/.github/workflows/`](../../projects/om-datacenter/.github/workflows/)
- 项目层 caller workflow 规范：[`../../pipeline/project-layer/caller-workflow-spec.md`](../../pipeline/project-layer/caller-workflow-spec.md)
- 凭据存储分档：[`../../pipeline/generic-layer/credentials-storage.md`](../../pipeline/generic-layer/credentials-storage.md)
