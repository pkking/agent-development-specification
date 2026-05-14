# 端到端流水线全景架构

> 本文档是**单文档完整入口**。读完这一份你应该能搞懂：
> - 每一阶段做什么（人 + AI）
> - 每一步用什么 prompt / 什么 runner / 什么 secret / 什么脚本 / 什么规范文档
> - 每一步在什么目录跑、回显长什么样、下一步是什么
> - 所有引用均为可点击的下钻链接

## 0. 一张图看懂全流程

```
[人] backlog 仓提 issue                              【阶段 1】
        │  → 模板 teams/templates/Requirement Analysis/
        │  → 规范 teams/context/team/issue-workflow-guide.md
        ▼
[人] maintainer 评 /accepts + 打 accepted 标签       【阶段 2】
        │  → 系统：backlog 仓 forward workflow 自动贴 [<服务名>需求] 菜单
        ▼
[人] 评论 [<服务名>需求] → 机器人贴菜单              【阶段 3】
        │  → 项目仓 projects/<project>/prompts/trigger-menu.md
        ▼
┌─────────────────────┬─────────────────────────────────┬─────────────────────────┐
│                     │                                 │                         │
▼                     ▼                                 ▼                         │
[人] 评 [<服务名>需求分析]  [人] 评 [<服务名>需求实现]    [人] 评 [<服务名>需求上线]    │
        │                       │                           │（白名单 maintainer）
        ▼【流程 1】              ▼【流程 2】                  ▼【流程 3】
   issue-1-analyze-           issue-2-implement-           issue-3-merge-
   requirement.yml            and-preview.yml              and-deploy.yml
   runner: ai-dev-runner      runner: ai-dev-runner        runner: ai-dev-runner
   timeout: 20 min            timeout: 90 min              timeout: 25 min
        │                       │                           │
   AI 写需求分析说明书           orchestrate.sh：             权限校验白名单
   → backlog 仓开 PR            ① design agent              → 找 head=<BRANCH> PR
   → 回评 issue 贴 PR 链接      ② dev agent                  → gh pr merge --squash
   （不级联，等人合入）          ③ deploy 起预览              → deploy.py promote
                                ④ tester agent              → deploy.py cleanup
                                ⑤ review/gate agent         → 回评 issue
                                多轮迭代（≤ MAX_FIX_ROUNDS）
                                → 回评 issue 2 条评论

    旁支：人工提 PR → caller workflow → pr-deploy-preview.yml (runs-on: k8s-deployer)
                                            → deploy.py 起预览 / cleanup
```

每个 box 都有详细的下钻文档。下面逐阶段表格化展开。

---

## 1. 阶段 1：人在 backlog 仓提 issue

| 项 | 内容 |
|---|---|
| 谁做 | 业务方 / 需求提出人 |
| 触发 | 访问 [`opensourceways/backlog`](https://github.com/opensourceways/backlog) issues → New Issue |
| 系统做啥 | 无（等 maintainer accept） |
| 模板 | [`../teams/templates/Requirement Analysis/`](../teams/templates/Requirement%20Analysis/) |
| 规范 | [`../teams/context/team/issue-workflow-guide.md`](../teams/context/team/issue-workflow-guide.md) §Stage 1 |
| 完成判据 | issue 已提交且打了对应需求模板 |
| 下一步 | 等 maintainer 评 `/accepts` |
| 详细 | [`stage-flow/stage-1-issue-submit.md`](stage-flow/stage-1-issue-submit.md) |

---

## 2. 阶段 2：maintainer accept

| 项 | 内容 |
|---|---|
| 谁做 | 产品经理 / 项目 maintainer |
| 触发 | 评论 `/accepts` + 打 `accepted` 标签 |
| 系统做啥 | backlog 仓 forward workflow 自动贴 `[<服务名>需求]` 菜单 |
| 触发的 workflow | backlog 仓 `forward.yml` |
| runner | GitHub-hosted `ubuntu-latest`（不用自托管）|
| runner 跑什么 | 调 `gh api` 给 issue 加菜单评论 |
| 评论模板 | [`../projects/<project>/prompts/trigger-menu.md`](../projects/) |
| 规范 | [`../teams/context/team/issue-workflow-guide.md`](../teams/context/team/issue-workflow-guide.md) §Stage 2 |
| 完成判据 | issue 收到「可用命令菜单」评论 |
| 下一步 | 评论 `[<服务名>需求分析]` 启动流程 1 |
| 详细 | [`stage-flow/stage-2-acceptance.md`](stage-flow/stage-2-acceptance.md) |

---

## 3. 阶段 3：评论 [<服务名>需求] 弹菜单

| 项 | 内容 |
|---|---|
| 谁做 | 任何参与人 |
| 触发 | issue 评论 `[<服务名>需求]`（如 `[数据中台需求]` / `[机器人需求]`）|
| 系统做啥 | 机器人贴一条「可用命令菜单」（列出 3 个后续触发词 + 各自作用）|
| 触发的 workflow | backlog 仓 forward workflow |
| runner | GitHub-hosted `ubuntu-latest` |
| 评论模板 | 项目专属：[`../projects/<project>/prompts/trigger-menu.md`](../projects/) |
| 规范 | [`pr-comment-protocol.md`](pr-comment-protocol.md) §菜单评论模板 |
| 完成判据 | issue 收到菜单评论 |
| 下一步 | 按菜单选触发词进入流程 1 / 2 / 3 |
| 详细 | [`stage-flow/stage-3-trigger-menu.md`](stage-flow/stage-3-trigger-menu.md) |

---

## 4. 流程 1：[<服务名>需求分析] — AI 写需求文档

**触发**：人在 issue 评论 `[<服务名>需求分析]`（或跨仓 dispatch `event_type=backlog_analyze`）

**触发的 workflow**：项目仓 `.github/workflows/issue-1-analyze-requirement.yml`
（骨架见 [`generic-layer/workflow-skeletons.md`](generic-layer/workflow-skeletons.md) §issue-1，
模板见 [`../projects/template/.github/workflows/caller-workflow.yml.tmpl`](../projects/template/.github/workflows/),
实例见 [`../projects/om-datacenter/.github/workflows/`](../projects/om-datacenter/.github/workflows/)）

**runner**：`self-hosted, ai-dev-runner`（K8s 里跑的 Pod）— 见 [`generic-layer/runners.md`](generic-layer/runners.md) §ai-dev-runner
部署 yaml 在 [`../src/runner/ai-dev-runner/deployment.yaml`](../src/runner/ai-dev-runner/deployment.yaml)

**Timeout**：20 min

**模式分流**（按 issue 标题）：
- `[需求]` → ra-doc 模式：写需求分析说明书 PR 到 backlog 仓
- `[任务]` / `[缺陷]` / 无关键字 → user-view 模式：仅在 issue 回「用户视角需求描述」

### ra-doc 模式步骤

| # | 步骤 | 在哪跑 | 用什么脚本 | 用什么 secret | 用什么规范 / 引用项目文档 | 期望回显 |
|---|---|---|---|---|---|---|
| 1 | Pre-clean workspace | `$GITHUB_WORKSPACE` | inline shell | - | - | `cleaned workspace` |
| 2 | Checkout 项目仓 | runner pod | `actions/checkout@v4` | `BACKLOG_REPO_TOKEN`（[规范](generic-layer/credentials-storage.md#github-secrets)）| [`../projects/<project>/CLAUDE.md`](../projects/) | `Cloned <repo>` |
| 3 | Decide A_MODE | runner pod | inline shell | - | issue 标题 | `A_MODE=ra-doc` 或 `user-view` |
| 4 | Setup opencode | runner pod | composite action（[runner Dockerfile](../src/runner/ai-dev-runner/Dockerfile)）| `OPENCODE_API_KEY` | - | `opencode ready` |
| 5 | Clone backlog → 切分支 → AI 写文档 | `/tmp/backlog-docs/` | opencode + agent `requirements-doc` | `BACKLOG_REPO_TOKEN` | 模板 [`../teams/templates/Requirement Analysis/`](../teams/templates/Requirement%20Analysis/) + 经验 [`../teams/context/experience/需求分析说明书编写经验.md`](../teams/context/experience/) | 文档落到 `opensourceways/<repo>/issue_docs/<N>/Requirement Analysis/` |
| 6 | push + 开 PR | `/tmp/backlog-docs/` | `gh pr create` | `BACKLOG_REPO_TOKEN` | [`pr-comment-protocol.md`](pr-comment-protocol.md) | `PR opened: https://github.com/.../pull/N` |
| 7 | 回评 issue 贴 PR 链接 | runner pod | `gh issue comment` | `BACKLOG_REPO_TOKEN` | [`pr-comment-protocol.md`](pr-comment-protocol.md) §流程 1 评论模板 | `Comment posted` |

**完成判据**：issue 收到 PR 链接评论；backlog 仓收到需求文档 PR

**下一步**：人评审 PR → 合入 → 评论 `[<服务名>需求实现]` 启动流程 2

**详细文档**：[`stage-flow/flow-1-requirement.md`](stage-flow/flow-1-requirement.md)

### user-view 模式（简版）

仅在 issue 回一段「用户视角需求描述」评论（含 `<!-- USER_VIEW_DOC -->` 锚点，供流程 2 读取），不开 PR、不级联。详细见 [`stage-flow/flow-1-requirement.md`](stage-flow/flow-1-requirement.md) §user-view 模式。

---

## 5. 流程 2：[<服务名>需求实现] — 4 agent 对抗 + 起预览

**触发**：人在 issue 评论 `[<服务名>需求实现]`（前提：需求文档 PR 已合入）

**触发的 workflow**：项目仓 `.github/workflows/issue-2-implement-and-preview.yml`

**runner**：`self-hosted, ai-dev-runner`，**timeout 90 min**

**核心编排脚本**：[`../src/orchestrator/orchestrate.sh`](../src/orchestrator/orchestrate.sh)
（设计见 [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md)）

### Workflow 入口步骤

| # | 步骤 | 在哪跑 | 用什么脚本 | 用什么 secret | 用什么规范 | 期望回显 |
|---|---|---|---|---|---|---|
| 1 | Pre-clean workspace | `$GITHUB_WORKSPACE` | inline shell | - | - | - |
| 2 | 算 `BRANCH=<source-repo 短名>-issue-<N>` | runner pod | inline shell | - | [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md) §分支命名 | `BRANCH=backlog-issue-123` |
| 3 | Checkout 项目仓 + 所有 submodule | runner pod | `actions/checkout@v4 --recurse-submodules` | `BACKLOG_REPO_TOKEN` | - | `Cloned <repo> + N submodules` |
| 4 | Setup opencode | runner pod | composite action | `OPENCODE_API_KEY` | - | `opencode ready` |
| 5 | Fetch issue 内容 | `/tmp/opencode/issue.txt` | composite action `fetch-issue` | `BACKLOG_REPO_TOKEN` | - | `issue.txt ready` |
| 6 | **调 `orchestrate.sh`**（核心）| `$GITHUB_WORKSPACE` | [`../src/orchestrator/orchestrate.sh`](../src/orchestrator/orchestrate.sh) | 见下方各 agent | 见下方 | 见下方 |

### orchestrate.sh 内部 4 agent 对抗（多轮迭代，最多 `MAX_FIX_ROUNDS=3` 轮）

| Agent | 输入 | 输出 | 用的 prompt | 用的项目规范 | 用的脚本 / 工具 |
|---|---|---|---|---|---|
| ① **design** | issue.txt + 项目仓 CLAUDE.md | `route.json` + `design.md`（验收标准）| [`../teams/prompts/architecture-design.md`](../teams/prompts/architecture-design.md) + [`../projects/<project>/prompts/flow-2-implement.md`](../projects/) | [`../projects/<project>/CLAUDE.md`](../projects/) + [`../projects/<project>/docs/architecture.md`](../projects/) | - |
| ② **dev** | design.md + 项目仓代码 | 改 dev 仓代码 + commit/push `<BRANCH>` + 开 PR + `result.json` | [`../teams/prompts/development.md`](../teams/prompts/development.md) | [`../teams/standards/coding.md`](../teams/standards/coding.md) + [`../projects/<project>/docs/coding-overrides.md`](../projects/) | `git` / `gh pr create` |
| ③ **deploy**（脚本非 agent） | 各 PR 列表 | nginx Ingress 预览 URL `https://<repo>-<PR>.ai.test.osinfra.cn/` | - | [`../projects/<project>/.preview/service.yaml`](../projects/) | [`../src/deployer/deploy.py`](../src/deployer/deploy.py) 4 种模式见 [`generic-layer/deployer.md`](generic-layer/deployer.md) |
| ④ **tester** | 各 PR + design.md 验收标准 | `test_report.md` / `test_fail.md` | [`../teams/prompts/test-strategy.md`](../teams/prompts/test-strategy.md) | [`../teams/standards/testing.md`](../teams/standards/testing.md) + [`testing-strategy.md`](testing-strategy.md) | [`../src/tests/run_layered.sh`](../src/tests/run_layered.sh) |
| ⑤ **review/gate** | 各 PR diff | `review_report.md` / `review_fail.md` | [`../teams/prompts/pr-comment.md`](../teams/prompts/pr-comment.md) | [`../teams/security-gates/`](../teams/security-gates/) 3 文档 | [`../src/gates/run.sh`](../src/gates/run.sh) 4 项检查见 [`generic-layer/gates.md`](generic-layer/gates.md) |
| **feedback** | tester/review 失败结果 | `feedback.md` 回 dev 重跑 | - | - | orchestrate.sh 内置逻辑 |

### Secret 列表（流程 2 用到）

| Secret | 用途 | 来源 |
|---|---|---|
| `BACKLOG_REPO_TOKEN` | 跨仓 clone / push / 开 PR | GitHub repo secret |
| `OPENCODE_API_KEY` | 4 个 agent 调 LLM | GitHub repo secret |
| `AI_TEST_KUBECONFIG` | deploy.py 调 K8s 起预览 | GitHub repo secret（base64） |
| `AES_KEY` / `AES_IV` | （add-community 特殊场景）解 PG token_pool | GitHub repo secret |

完整凭据规范见 [`generic-layer/credentials-storage.md`](generic-layer/credentials-storage.md)。

### 收尾

- 回评 issue 2 条评论：
  - 第 1 条（部署完成）：改动点 + 各 PR 预览 URL + 调用示例
  - 第 2 条（完整结果）：评审 + 测试 + 验收
- 写 `docs/change_logs/<date>-<source-repo>-issue-<N>.md` 归档
- 评论模板：[`pr-comment-protocol.md`](pr-comment-protocol.md) §流程 2 评论模板

**完成判据**：issue 收到 2 条回评 + 每个 dev 仓有 head=`<BRANCH>` 的 open PR + 预览 URL 可访问

**下一步**：人看预览 → 满意 → maintainer 评论 `[<服务名>需求上线]`；不满意 → 再评 `[<服务名>需求实现]` 换行写改动点，二轮在原分支接着改

**详细文档**：[`stage-flow/flow-2-implementation.md`](stage-flow/flow-2-implementation.md)

---

## 6. 流程 3：[<服务名>需求上线] — 合入 + 上 beta + 清理

**触发**：maintainer 评论 `[<服务名>需求上线]`（**仅白名单用户**，见 [`release-process.md`](release-process.md) §白名单管理）

**触发的 workflow**：项目仓 `.github/workflows/issue-3-merge-and-deploy.yml`

**runner**：`self-hosted, ai-dev-runner`，**timeout 25 min**

### 步骤

| # | 步骤 | 用什么脚本 | 用什么 secret | 用什么规范 | 期望回显 |
|---|---|---|---|---|---|
| 1 | 权限校验：trigger user ∈ 白名单 | inline shell | `BACKLOG_REPO_TOKEN` | [`release-process.md`](release-process.md) §白名单 | `✓ user=<X> allowed` 或 fail |
| 2 | 找各 dev 仓 head=`<BRANCH>` open PR | `gh pr list` | `BACKLOG_REPO_TOKEN` | - | 列出 N 个 PR |
| 3 | 门禁：mergeable / 无冲突 | `gh pr view` | `BACKLOG_REPO_TOKEN` | [`../teams/standards/release.md`](../teams/standards/release.md) | `✓ all mergeable` |
| 4 | 逐 PR `gh pr merge --squash --delete-branch` | `gh pr merge` | `BACKLOG_REPO_TOKEN` | [`../teams/standards/git-workflow.md`](../teams/standards/git-workflow.md) §合入策略 | `Merged #N` |
| 5 | 逐仓 `deploy.py promote --env beta`（触发 Jenkins job 上线）| [`../src/deployer/deploy.py`](../src/deployer/deploy.py) | `JENKINS_API_USER` / `JENKINS_API_TOKEN` / `AI_TEST_KUBECONFIG` | [`generic-layer/deployer.md`](generic-layer/deployer.md) §promote | `Promoted <repo> to beta, build #N` |
| 6 | 逐 PR `deploy.py cleanup`（删预览资源）| `deploy.py cleanup` | `AI_TEST_KUBECONFIG` | [`generic-layer/deployer.md`](generic-layer/deployer.md) §cleanup | `Cleaned preview for PR #N` |
| 7 | 回评 issue 上线结果 | `gh issue comment` | `BACKLOG_REPO_TOKEN` | [`pr-comment-protocol.md`](pr-comment-protocol.md) §流程 3 评论模板 | `Comment posted` |

**完成判据**：所有相关 PR 已 merge + 各仓主部署已 rollout 到 beta + 预览资源全部清理

**下一步**：beta 验证 → 生产发布（由项目独立的发布流程负责，不在本流水线范围）

**详细文档**：[`stage-flow/flow-3-release.md`](stage-flow/flow-3-release.md)

---

## 7. 旁支：人工提 PR 预览（不走需求流）

**触发**：项目 dev 仓 PR opened / synchronize / closed

**触发的 workflow**：
1. 项目仓 caller workflow → `repository_dispatch event_type=pr_deploy`（项目仓的 [`caller-workflow.yml`](../projects/template/.github/workflows/caller-workflow.yml.tmpl)）
2. 通用层 `pr-deploy-preview.yml`（响应 `pr_deploy` 事件）

**runner**：`self-hosted, k8s-deployer`（注意不是 ai-dev-runner）— 见 [`generic-layer/runners.md`](generic-layer/runners.md) §k8s-deployer

**步骤**：调 [`../src/deployer/deploy.py`](../src/deployer/deploy.py) deploy → 预览 URL 自动评论到 PR；PR closed 时触发 `pr_deploy_cleanup`

**详细文档**：[`stage-flow/flow-2-implementation.md`](stage-flow/flow-2-implementation.md) §旁支

---

## 8. 故障 / 回滚 / 复盘

- 上线后异常 → 见 [`release-process.md`](release-process.md) §回滚
- 复盘文档模板 → [`../teams/templates/Learn From the Incident/`](../teams/templates/Learn%20From%20the%20Incident/)
- 复盘经验 → [`../teams/context/experience/`](../teams/context/experience/)

---

## 9. 关键约定速查

| 约定 | 值 | 文档 |
|---|---|---|
| Workflow runner 标签 | `self-hosted, ai-dev-runner` / `self-hosted, k8s-deployer` | [`generic-layer/runners.md`](generic-layer/runners.md) |
| Workflow B 分支命名 | `<source-repo 短名>-issue-<N>` | [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md) |
| 预览 URL 格式 | `https://<repo-full-name>-<PR-number>.ai.test.osinfra.cn/` | [`generic-layer/deployer.md`](generic-layer/deployer.md) |
| 触发评论前缀 | `[<服务名>需求分析]` / `[<服务名>需求实现]` / `[<服务名>需求上线]` | 各流程文档 |
| 报告归档目录 | `opensourceways/<repo>/issue_docs/<issueId>/{阶段}/` | [`stage-flow/flow-1-requirement.md`](stage-flow/flow-1-requirement.md) |
| 多 agent 对抗轮数 | `MAX_FIX_ROUNDS=3`（GitHub Variables 可调） | [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md) |
| Workflow B timeout | 90 min（按场景可调） | [`generic-layer/workflow-skeletons.md`](generic-layer/workflow-skeletons.md) |
| 凭据存储 | GitHub Secret + K8s Secret + Vault sidecar | [`generic-layer/credentials-storage.md`](generic-layer/credentials-storage.md) |

---

## 10. 接下来

- 想接入新项目 → [`project-layer/onboarding-tier-B.md`](project-layer/onboarding-tier-B.md) 5 步走完
- 想理解 4 agent 怎么对抗 → [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md) + [`generic-layer/agents.md`](generic-layer/agents.md)
- 想理解部署器 4 种模式 → [`generic-layer/deployer.md`](generic-layer/deployer.md)
- 想理解凭据怎么存 → [`generic-layer/credentials-storage.md`](generic-layer/credentials-storage.md)
- 想理解写需求文档时 AI 怎么协作 → [`../teams/context/experience/AI辅助需求分析工作模式.md`](../teams/context/experience/AI辅助需求分析工作模式.md)
