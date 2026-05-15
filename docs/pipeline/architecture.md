# 端到端流水线全景架构

> **单文档完整入口**。读完这一份你应该能搞懂：
> - 每一阶段做什么（人 + AI），每一步用什么 prompt / 必读什么文档 / 落地到哪里 / 下一步是什么
> - 所有引用均为可点击的内部链接（不引外部仓库 URL）
> - 想看更细节的，每段末尾有「详细」链接深入

## 0. 一张图看懂全流程

```
[人] backlog 仓提 issue                                    【阶段 1】
        │  → 模板：Feature Request / Bug Report
        ▼
[人] maintainer 评 /accepts + 打 accepted 标签             【阶段 2】
        │  → 系统：backlog 仓 forward workflow 自动贴菜单
        ▼
[人] 评论 [<服务名>需求] → 机器人贴 3 流程菜单              【阶段 3】
        ▼
┌─────────────────────┬─────────────────────────────────┬─────────────────────────┐
▼                     ▼                                 ▼
[人] 评 [<服务名>需求分析]  [人] 评 [<服务名>需求实现]    [人] 评 [<服务名>需求上线]
        │                       │                           │（白名单 maintainer）
        ▼【流程 1】              ▼【流程 2】                  ▼【流程 3】
   issue-1-analyze-           issue-2-implement-           issue-3-merge-
   requirement.yml            and-preview.yml              and-deploy.yml
        │                       │                           │
   AI 写需求分析说明书           orchestrate.sh：             权限校验白名单
   → backlog 仓开 PR            ① design agent              → merge 各 dev 仓 PR
   → 回评 issue 贴 PR 链接      ② dev agent                  → deployer promote 到 beta
   （等人合入）                 ③ deploy 起预览              → deployer cleanup 预览
                                ④ tester + review            → 回评 issue
                                多轮迭代（≤ MAX_FIX_ROUNDS）

    旁支：人工提 PR → caller workflow → pr-deploy-preview.yml → deploy.py
```

---

## 0.5 前置：Runner 怎么部署的（一次性，先于任何流水线）

> 流水线开跑前，团队 SRE 已经把两类 self-hosted runner 部署在内部 K8s 集群里、并注册到 GitHub。流程 1/2/3 跑起来时，工作负载直接调度到这两类 pod 上。
> **业务方 / 普通开发者不接触这段**，只有团队 SRE / 平台 owner 第一次接入或扩容 / 升级时才动。
> **完整的 runner 单文档入口**：[`generic-layer/runners.md`](generic-layer/runners.md) — 部署 / 镜像组件 / 凭据 / 资源 / 升级 / 故障排查全在那一份。

### 0.5.1 两类 runner

| Runner | 跑什么 | runs-on 标签 | 副本数（参考） | 文档锚点 |
|---|---|---|---|---|
| `ai-dev-runner` | 流程 1 / 2 / 3 主体（4 agent 对抗 / orchestrate.sh / gates / tester） | `[self-hosted, ai-dev-runner]` | 3 | [runners.md §2](generic-layer/runners.md#2-ai-dev-runner) |
| `k8s-deployer` | 起 / 清理预览部署（PR preview / 流程 3 promote / `deploy.py`） | `[self-hosted, k8s-deployer]` | 2 | [runners.md §3](generic-layer/runners.md#3-k8s-deployer) |

### 0.5.2 部署方式（要点 — 详细见 [runners.md §2.1](generic-layer/runners.md#21-部署方式架构)）

K8s `Deployment` + `ServiceAccount` + `RBAC` + `ConfigMap` + `Secret`；**镜像由本仓 Dockerfile 构建**，不用 actions-runner-controller / 不用 Helm chart。

代码与 yaml 在 [`../src/runner/`](../src/runner/) 下，各文件作用：[runners.md §2.1 文件清单](generic-layer/runners.md#21-部署方式架构)。

### 0.5.3 部署步骤（5 步 — 详细见 [runners.md §2.3](generic-layer/runners.md#23-部署步骤团队-sre-一次性跑一遍)）

```
1. 构建镜像     →  src/runner/ai-dev-runner/build-and-push.sh
2. 拿 GitHub registration token
3. 建 ns + 注入 Secret
4. 应用 RBAC → ConfigMap → Deployment
5. 验证 runner online（GitHub Settings 看，或 kubectl get pod 看）
```

k8s-deployer 同样跑一遍，差异见 [runners.md §3.4](generic-layer/runners.md#34-部署步骤)。

### 0.5.4 镜像组件清单（详细见 [runners.md §2.2](generic-layer/runners.md#22-镜像组件清单)）

ai-dev-runner 装的：Ubuntu 24.04 底座 + 系统包 + `build-essential` / `python3` / `nodejs/npm` / `openjdk-17 + maven` / `kubectl` / `helm` / `gh` / Claude CLI（或 opencode）/ `actions/runner` v2.317.0 + 非 root `runner` 用户。

k8s-deployer 不装 Node / Java / Claude CLI / build-essential（最小镜像，详见 [runners.md §3.3](generic-layer/runners.md#33-镜像组件清单差异处)）。

### 0.5.5 部署 vs 流水线时序

```
[团队 SRE 一次性做] 部署 ai-dev-runner + k8s-deployer 到 K8s
       ↓ (runner pod 持续 online 等单)
[业务方] 在 backlog 提 issue                ← 阶段 1
[maintainer] /accepts                       ← 阶段 2
[人] 评 [<服务名>需求...]                    ← 阶段 3
       ↓
GitHub Actions 把 job 派给 label 匹配的 online runner pod
       ↓
runner pod 在 $GITHUB_WORKSPACE 跑 yml 步骤
```

**runner 不每次 job 重新部署** — 长驻 pod，registration token 一次性，过期由 entrypoint 自动重新 register。

### 0.5.6 升级 / 扩容 / 故障（详细见 [runners.md §2.8](generic-layer/runners.md#28-升级--扩容--故障排查)）

| 场景 | 操作 |
|---|---|
| 升级镜像 | `build-and-push.sh` → `kubectl set image` |
| 扩容 | `kubectl scale deployment/ai-dev-runner --replicas=N` |
| runner 卡死 | `kubectl delete pod -l app=ai-dev-runner` |
| 凭据轮换 | 更新 Secret → `kubectl rollout restart` |

---

## 1. 阶段 1：人在 backlog 仓提 issue

**谁做**：业务方 / 需求提出人

**怎么做**：进 backlog 仓 → New Issue → 按需求类型选模板填写：

- 标题含 `[需求]` → 选 [`Feature Request.md`](../teams/templates/Issue%20Submission/Feature%20Request.md)
- 标题含 `[缺陷]` / `[任务]` → 选 [`Bug Report.md`](../teams/templates/Issue%20Submission/Bug%20Report.md)

两份模板的索引和选择规则：[`../teams/templates/Issue Submission/README.md`](../teams/templates/Issue%20Submission/README.md)

**完成判据**：issue 已提交，正文按模板填全。

**下一步**：等 maintainer 评 `/accepts` → 进阶段 2。

**详细**：[`stage-flow/stage-1-issue-submit.md`](stage-flow/stage-1-issue-submit.md)

---

## 2. 阶段 2：maintainer accept

**谁做**：产品经理 / 项目 maintainer

**怎么做**：在 issue 评论 `/accepts`，并打 `accepted` 标签。

**系统做什么**：backlog 仓的 **forward workflow** 自动在该 issue 上贴一条菜单评论，列出 3 个后续触发词。

> **forward workflow 是什么** — 跨仓事件转发器。`accepted` 标签 + `[<服务名>需求]` 评论的组合触发它「贴菜单 + 把后续触发词转发到 umbrella 仓」。完整说明见 [`../teams/external-workflows/README.md`](../teams/external-workflows/README.md)，源码见 [`forward-to-datacenter.yml`](../teams/external-workflows/forward-to-datacenter.yml)。

**评论模板（菜单评论的项目专属版本）**：项目层 prompt，例如：

- 模板（任意新项目）：[`../projects/template/prompts/trigger-menu.md.tmpl`](../projects/template/prompts/trigger-menu.md.tmpl)
- 实例：[`../projects/om-datacenter/prompts/trigger-menu.md`](../projects/om-datacenter/prompts/trigger-menu.md)

**完成判据**：issue 上出现菜单评论。

**下一步**：评论 `[<服务名>需求]` 弹完整菜单 → 阶段 3；或直接评 `[<服务名>需求分析]` → 流程 1。

**详细**：[`stage-flow/stage-2-acceptance.md`](stage-flow/stage-2-acceptance.md)

---

## 3. 阶段 3：评论 `[<服务名>需求]` 弹菜单

**谁做**：任何参与人

**怎么做**：在 issue 评论 `[<服务名>需求]`（例 `[数据中台需求]` / `[小数需求]`）。

**系统做什么**：backlog 仓的 forward workflow 贴一条菜单评论，列出可用命令；后续 `[<服务名>需求分析]`/`[实现]`/`[上线]` 评论也由它转发到 umbrella 仓的 issue-1/2/3 yml。详见 [`../teams/external-workflows/README.md`](../teams/external-workflows/README.md)。

**评论模板**：

- 模板（任意新项目）：[`../projects/template/prompts/trigger-menu.md.tmpl`](../projects/template/prompts/trigger-menu.md.tmpl)
- 实例：[`../projects/om-datacenter/prompts/trigger-menu.md`](../projects/om-datacenter/prompts/trigger-menu.md)

**评论格式规范**：[`pr-comment-protocol.md`](pr-comment-protocol.md) §菜单评论模板

**完成判据**：issue 收到菜单评论。

**下一步**：按菜单选触发词，进入流程 1 / 2 / 3。

**详细**：[`stage-flow/stage-3-trigger-menu.md`](stage-flow/stage-3-trigger-menu.md)

---

## 3.5 Runner 内的路径约定（流程 1/2/3 共用）

ai-dev-runner 跑在 K8s pod 里、以非 root 用户 `runner` 运行（见 [`../src/runner/ai-dev-runner/Dockerfile`](../src/runner/ai-dev-runner/Dockerfile)），workflow 步骤里出现的几个路径变量都对应到容器内的实际位置：

| 变量 / 路径 | 实际位置（容器内） | 干啥用 | 出处 |
|---|---|---|---|
| `$HOME` | `/home/runner` | runner 用户家目录，`opencode` 的 `auth.json` / `config` 放这里 | Dockerfile `USER runner`、yml `env.HOME` |
| actions-runner 安装目录 | `/home/runner/actions-runner/` | GitHub Actions runner 自己的代码 + `_work/` 子目录 | Dockerfile `Install GitHub Actions runner` 段 |
| `$GITHUB_WORKSPACE` | `/home/runner/actions-runner/_work/<repo>/<repo>` | actions-runner 默认 workdir，**`actions/checkout` 把 umbrella 仓拉到这里**；流程 1 / 2 / 3 的所有 inline shell 默认在此跑 | actions-runner `--work _work` 参数 |
| `$WORKSPACE_DIR`（仅流程 2） | `/workspaces/<handling-repo>/<source-short>-issue-<N>` | per-issue 独立工作区，**挂 PVC**，跨 job 复用；orchestrate.sh 在这里 `git submodule update` 拉 dev 子仓 | yml 的 `Setup opencode env` step（[issue-2 line 97-108](../projects/om-datacenter/.github/workflows/issue-2-implement-and-preview.yml)）|
| `$WORK_DIR`（agent 内可见） | = `$WORKSPACE_DIR` | dev / tester / review agent 在这里改/读 dev 子仓代码 | orchestrate.sh 内 export |
| `$TOOLS_DIR`（agent 内可见） | = `$GITHUB_WORKSPACE` | 流水线工具仓（umbrella 自己的 `src/` / `.github/agents/`） | orchestrate.sh 内 export |
| `/tmp/opencode/` | runner pod tmpfs | agent 间传文件（`issue.txt` / `route.json` / `design.md` / `result.json` / `feedback.md` / `deploy/pr-<N>.json` ...） | 各 agent prompt 约定 |

**为什么要分 `GITHUB_WORKSPACE` 和 `WORKSPACE_DIR`**：

- `$GITHUB_WORKSPACE` 由 GitHub Actions 管，每个 job 起来时 actions-runner 会清理它，**装不下跨 job 持久状态**
- 流程 2 跑 90 min、要管 5 个 dev 仓的 checkout / submodule，需要重跑时能复用，所以单独搞一个 PVC 挂的 `/workspaces/.../` 路径，按「umbrella 仓 / per-issue」切目录互不打架

**PVC 配置**：见 [`../src/runner/ai-dev-runner/deployment.yaml`](../src/runner/ai-dev-runner/deployment.yaml) 的 `volumeMounts` 段（`/workspaces` 挂 PersistentVolumeClaim）。

---

## 4. 流程 1：`[<服务名>需求分析]` — AI 写需求文档

**触发**：人在 issue 评论 `[<服务名>需求分析]`。

**workflow 文件**：[`../projects/om-datacenter/.github/workflows/issue-1-analyze-requirement.yml`](../projects/om-datacenter/.github/workflows/issue-1-analyze-requirement.yml)
（runner：`self-hosted, ai-dev-runner`；timeout：20 min）

### 4.1 按 issue 标题分两种模式

| issue 标题 | 模式 | 产出 |
|---|---|---|
| 含 `[需求]` | **ra-doc** | 在 backlog 仓开一份「需求分析说明书」PR，等人评审合入 |
| 含 `[任务]` / `[缺陷]` / 无关键字 | **user-view** | 只在 issue 回一段「用户视角需求描述」评论（含 `<!-- USER_VIEW_DOC -->` 锚点，给流程 2 用），不开 PR |

分流逻辑：见 workflow 的 `Decide A_MODE` 步骤。

### 4.2 ra-doc 模式步骤

1. **Workflow checkout 项目仓**（umbrella 仓，作为 TOOLS_DIR），不拉 submodule；落到 `$GITHUB_WORKSPACE`，含**项目 CLAUDE.md**（[模板 `CLAUDE.md.tmpl`](../projects/template/CLAUDE.md.tmpl) / 实例 [om-datacenter/CLAUDE.md](../projects/om-datacenter/CLAUDE.md)）+ `.github/agents/` + `skills/` + `docs/`
2. **算路径**：`DOCS_BRANCH=issue-<N>-design-docs`，目标文件路径 `opensourceways/<source-repo-short>/issue_docs/<N>/Requirement Analysis/#<N> Requirement Analysis Specification.md`
3. **Setup opencode env**（装 LLM 调用器，密钥来自 [`OPENCODE_API_KEY`](generic-layer/credentials-storage.md)）
4. **Clone backlog 仓**到 `$GITHUB_WORKSPACE/backlog`（实际路径 `/home/runner/actions-runner/_work/<repo>/<repo>/backlog`，见 §3.5），新建（或复用）`DOCS_BRANCH`
5. **Fetch issue 全文**（标题 + 正文 + 全部评论）到 `/tmp/opencode/issue.txt`，由 composite action `.github/actions/fetch-issue` 完成
6. **准备项目 context — agent 写需求分析得先看懂项目是什么**（关键！否则 agent 凭空臆想需求）：
   - **项目 CLAUDE.md**：`$GITHUB_WORKSPACE/CLAUDE.md`（umbrella 仓根）— **项目 1 分钟读懂入口**：模板见 [`../projects/template/CLAUDE.md.tmpl`](../projects/template/CLAUDE.md.tmpl)，实例见 [`../projects/om-datacenter/CLAUDE.md`](../projects/om-datacenter/CLAUDE.md)。覆盖：项目电梯陈词 / 架构图 / 技术栈 / 仓结构 / 项目铁规 / 踩坑录 / 流水线接入 / 词汇表 / owner / 索引
   - **项目架构详尽**：`$GITHUB_WORKSPACE/docs/architecture.md`（如有）
   - **项目 skills**：`$GITHUB_WORKSPACE/skills/`（项目专属操作 playbook）
   - **各 dev 子仓的 CLAUDE.md**（如 umbrella 项目）：通过 submodule 路径访问；不需要全部 clone，根据 issue 涉及的子仓有选择性读
7. **跑 AI agent 写文档**（核心一步）：
   - 加载 prompt：[`../projects/om-datacenter/.github/agents/requirements-doc.md`](../projects/om-datacenter/.github/agents/requirements-doc.md)（其中已 require「先读 `$GITHUB_WORKSPACE/CLAUDE.md` 弄清楚项目是什么再动笔」）
   - 工作目录 = backlog 仓 checkout（agent 能直接读到 backlog 的 `templates/` / `AGENTS.md` / `context/`），同时通过绝对路径 `$GITHUB_WORKSPACE/CLAUDE.md` 读项目 context
   - agent 按 prompt 强制必读 3 类文件：
     - **项目 context**（step 6 列的那几个）→ 知道这是什么项目、要符合哪些项目铁规
     - **团队需求分析模板** [`../teams/templates/Requirement Analysis/`](../teams/templates/Requirement%20Analysis/) → 知道文档结构
     - **写作经验**：[`../teams/context/experience/需求分析说明书编写经验.md`](../teams/context/experience/%E9%9C%80%E6%B1%82%E5%88%86%E6%9E%90%E8%AF%B4%E6%98%8E%E4%B9%A6%E7%BC%96%E5%86%99%E7%BB%8F%E9%AA%8C.md) + [AI 辅助工作模式](../teams/context/experience/AI%E8%BE%85%E5%8A%A9%E9%9C%80%E6%B1%82%E5%88%86%E6%9E%90%E5%B7%A5%E4%BD%9C%E6%A8%A1%E5%BC%8F.md) → 避免之前踩过的坑
   - agent 按模板结构填写：场景 / 验收标准（可量化）/ 核心逻辑 / 任务清单（2-4 个）/ 需求相关性分析（need_security / need_design / need_itest / need_ux / need_light）/ 价值评估（Accept / Reject / Pending）
8. **Commit + push docs 分支 → 开 PR 到 backlog 仓**：分支 `issue-<N>-design-docs`，base `main`
9. **回评原 issue**：贴 PR 链接 + 下一步说明（合入 PR 后评 `[<服务名>需求实现]`）

**完成判据**：issue 收到 PR 链接评论；backlog 仓收到需求文档 PR。

**下一步**：人评审 PR → 合入 → 评论 `[<服务名>需求实现]` 启动流程 2。

### 4.3 user-view 模式步骤

1-5 与 ra-doc 相同（只是不 clone backlog 仓）
6. **跑 AI agent 写极简用户视角描述**（prompt 内嵌在 yml 中），写到 `/tmp/opencode/user_view.md`
7. **回评原 issue**：贴用户视角描述（含 `<!-- USER_VIEW_DOC -->` 锚点）+ 下一步说明

**完成判据**：issue 收到一条带锚点的用户视角描述评论。

**下一步**：评 `[<服务名>需求实现]` 启动流程 2（flow-2 会自动从 issue 评论中抠出锚点段当需求文档）。

### 4.4 用到的 secret

| Secret | 用途 |
|---|---|
| `OPENCODE_API_KEY` | AI agent 调 LLM |
| [`BACKLOG_REPO_TOKEN`](generic-layer/credentials-storage.md)（或 `CROSS_REPO_TOKEN`） | clone backlog、push docs 分支、开 PR、回评 issue |

凭据档位见 [`generic-layer/credentials-storage.md`](generic-layer/credentials-storage.md)。

**详细**：[`stage-flow/flow-1-requirement.md`](stage-flow/flow-1-requirement.md)

---

## 5. 流程 2：`[<服务名>需求实现]` — 4 agent 对抗 + 起预览

**触发**：人评论 `[<服务名>需求实现]`（前提：流程 1 的需求 PR 已合入，或 user-view 模式已留下锚点评论）。

**workflow 文件**：[`../projects/om-datacenter/.github/workflows/issue-2-implement-and-preview.yml`](../projects/om-datacenter/.github/workflows/issue-2-implement-and-preview.yml)
（runner：`self-hosted, ai-dev-runner`；timeout：90 min）

### 5.1 入口步骤（yml 里做的事）

> 路径变量含义见 §3.5「Runner 内的路径约定」。本节里 `$GITHUB_WORKSPACE` = `/home/runner/actions-runner/_work/<repo>/<repo>`；`$WORKSPACE_DIR` = `/workspaces/<umbrella>/<source-short>-issue-<N>`（PVC 挂载）。

1. **Pre-clean workspace**：清 `$GITHUB_WORKSPACE`（GitHub-managed 默认 workdir）
2. **算名字**：`BRANCH=<source-repo 短名>-issue-<N>`（所有 dev 仓都用它）
3. **Checkout umbrella（om-datacenter）**：拉到 `$GITHUB_WORKSPACE`，不拉 submodule，要 `fetch-depth: 0`
4. **Init dev submodules**：从 `.gitmodules` 枚举所有 submodule 路径，逐个 `git submodule update --init`（落到 `$GITHUB_WORKSPACE/<submodule-path>/`；拉不下来的 dev 仓跳过，agent 后续会处理）
5. **Configure git**：设置 user/email + token-injected url rewrite
6. **Setup opencode env**：建 PVC 工作区 `$WORKSPACE_DIR=/workspaces/<handling-repo>/<source-short>-issue-<N>`；`opencode` 的 auth 写到 `$HOME/.local/share/opencode/auth.json`（即 `/home/runner/.local/share/opencode/auth.json`）
7. **Fetch issue 全文**：composite action `fetch-issue` 写到 `/tmp/opencode/issue.txt`
8. **准备需求文档** → `/tmp/opencode/requirement_analysis.md`：
   - `[需求]` 类：从 backlog 仓拉已合入的 `Requirement Analysis Specification.md`（拉不到 → 报错让人先合 PR）
   - `[任务]`/`[缺陷]`/无关键字：从 `/tmp/opencode/issue.txt` 抠 `<!-- USER_VIEW_DOC -->` 段
9. **调 orchestrate.sh**（核心循环，下一节展开）

### 5.2 orchestrate.sh 的 4 agent 对抗

脚本（om-datacenter 仓的 `src/orchestrate.sh`，spec 仓对应版本在 [`../src/orchestrator/orchestrate.sh`](../src/orchestrator/orchestrate.sh)）跑最多 `MAX_FIX_ROUNDS=3` 轮以下循环：

| # | Agent | prompt 文件 | 必读项目 CLAUDE.md | 输入 | 输出 |
|---|---|---|---|---|---|
| ① | **design** | [`../projects/om-datacenter/.github/agents/design.md`](../projects/om-datacenter/.github/agents/design.md) | umbrella [`../projects/om-datacenter/CLAUDE.md`](../projects/om-datacenter/CLAUDE.md) + 各 dev 子仓自己的 `CLAUDE.md`（在 `$WORKSPACE_DIR/<submodule>/CLAUDE.md`） | issue.txt + requirement_analysis.md | `/tmp/opencode/route.json`（路由 + target_repos）+ `/tmp/opencode/design.md`（含可量化验收标准） |
| ② | **dev** | [`../projects/om-datacenter/.github/agents/dev.md`](../projects/om-datacenter/.github/agents/dev.md) | 同上（umbrella + 各 dev 子仓） | design.md + route.json | 改各 dev 仓代码 + commit/push `<BRANCH>` + 开 PR + `/tmp/opencode/result.json` + `change_summary.md` |
| ③ | **deploy**（脚本非 agent） | [`../src/deployer/deploy.py`](../src/deployer/deploy.py) — 详见 §5.2.4 | — | result.json 的 PR 列表 + [`.preview/service.yaml`](project-layer/preview-service-yaml-spec.md) | 各 PR 一个 nginx Ingress 预览 URL；写 `/tmp/opencode/deploy/pr-<N>.json` |
| ④ | **tester** | [`../projects/om-datacenter/.github/agents/tester.md`](../projects/om-datacenter/.github/agents/tester.md) | 同上 | design.md 验收标准 + 各 PR 预览 + apimagic_endpoints | `test_report.md`（4 类测试逐项）+ `test_fail.md`（打回清单）+ `test_retro.md` |
| ⑤ | **review** | [`../projects/om-datacenter/.github/agents/review.md`](../projects/om-datacenter/.github/agents/review.md) | 同上 | 各 PR diff + gates 结果 | `review_report.md` + `review_fail.md`（打回清单） |
| feedback | — | — | — | tester + review 的打回清单 | 合成 `/tmp/opencode/feedback.md` 回给 dev / design 重跑 |

**全过 → 跳出循环；任一打回 → 回 dev（或 design）下一轮**，最多 `MAX_FIX_ROUNDS` 轮。

### 5.2.5 项目 CLAUDE.md — 在哪里、长什么样、谁写

每个 agent 在 prompt 里都写「**必读项目 CLAUDE.md**」，指的是这两层：

| 层 | 位置 | 谁维护 | 干啥用 |
|---|---|---|---|
| umbrella（项目主仓） | 项目仓根 `/CLAUDE.md`，spec 仓实例 [`../projects/om-datacenter/CLAUDE.md`](../projects/om-datacenter/CLAUDE.md) | 项目 owner | 写**项目级铁规** + 触发词 + 子仓清单 + 部署模式 + 白名单 + 凭据指引 + 覆盖团队规范的部分 |
| 各 dev 子仓 | 各 dev 子仓根 `/CLAUDE.md`（如 `APIMagic/CLAUDE.md`、`datastat-manage-website/CLAUDE.md`） | 各 dev 子仓 owner | 写**子仓级铁规** + 基础分支 + 敏感文件 git-ignore 清单 + 子仓特有的代码约定（如 APIMagic 的 `.ms` 写法） |

**runner 内的实际路径**：

- umbrella CLAUDE.md → `$GITHUB_WORKSPACE/CLAUDE.md`（actions/checkout 后落到这里）
- dev 子仓 CLAUDE.md → `$WORKSPACE_DIR/<submodule>/CLAUDE.md`（流程 2 setup 后 `git submodule update` 落到这里）

`$GITHUB_WORKSPACE` / `$WORKSPACE_DIR` 的实际路径见 §3.5。

**新项目接入怎么写自己的 CLAUDE.md**：

1. **模板（直接复制改）**：[`../projects/template/CLAUDE.md.tmpl`](../projects/template/CLAUDE.md.tmpl) — 含全部占位符（`<<PROJECT_NAME>>` / `<<TRIGGER_PREFIX>>` / `<<DEV_REPOS>>` / `<<DEPLOY_MODE>>` / `<<BASE_DOMAIN>>` / `<<NAMESPACE>>` / `<<MAINTAINER_WHITELIST>>`），按 [`../projects/template/ONBOARDING-CHECKLIST.md`](../projects/template/ONBOARDING-CHECKLIST.md) 逐字替换
2. **规范（必含哪些段、写法约束）**：[`project-layer/claude-md-spec.md`](project-layer/claude-md-spec.md) — 列出必含 8 段（项目档位 / 触发词 / 子仓清单 / 部署模式 / 白名单 / 凭据清单链接 / 项目铁规 / 覆盖团队规范的部分）+ 与三层规范继承关系
3. **真实参考**：[`../projects/om-datacenter/CLAUDE.md`](../projects/om-datacenter/CLAUDE.md) — 已完整接入的 B 档项目示例

**三层规范继承**（CLAUDE.md 之间的优先级）：

```
个人层 ~/.claude/CLAUDE.md      最高，本机生效，可覆盖项目/团队规范
    ↑
项目层 projects/<project>/CLAUDE.md  ← 本节讨论的就是这一层（umbrella 那份）
    ↑
团队层 ../teams/CLAUDE.md        所有项目共用底层规范
```

详尽规则与示例：[`../teams/CLAUDE.md`](../teams/CLAUDE.md) 顶部段。

### 5.2.4 deploy 这一步到底干了什么（脚本非 agent）

> deploy 是 orchestrate.sh 在 dev 产出 PR 后、review/tester 跑之前调的脚本，不是 agent。**完整文档**：[`generic-layer/deployer.md`](generic-layer/deployer.md)（10 节，覆盖入参/出参/模式/模板/清理/promote/谁跑它）。

**调用方**：`orchestrate.sh` 读 `/tmp/opencode/result.json` 的 PR 列表，对每个 PR 跑一次：

```
python3 src/deployer/deploy.py \
    --project   <project> \
    --service   <service> \
    --mode      <dev-pod|data-pod|shared|none>   # 由 .preview/service.yaml deploy_mode 决定
    --image     <registry>/<repo>:<pr-tag> \
    --pr-number <N> \
    --namespace <NAMESPACE> \
    --base-domain <BASE_DOMAIN>                  # 如 ai.test.osinfra.cn
  > /tmp/opencode/deploy/pr-<N>.json
```

**deploy.py 内部 7 步**（详细见 [deployer.md §4](generic-layer/deployer.md#4-详细部署流程)）：

```
1. 读 .preview/service.yaml             ← 项目仓配置入口
2. 选模板（src/deployer/templates/<mode>/）
3. 渲染（替换 ${PROJECT} / ${PR_NUMBER} / ${IMAGE_FULL} / ${NAMESPACE} / ${BASE_DOMAIN}）
4. kubectl apply                        ← 用 KUBECONFIG secret
5. kubectl wait readiness               ← 默认 120s
6. 收集 preview URL + ClusterIP + pod 状态 → JSON 输出到 stdout
7. 失败 → kubectl describe + pod logs tail 进 report 字段
```

**预览资源命名**：`preview-<service>-pr<N>`（Deployment / Service / Ingress 同名；Ingress host = `<service>-<N>.<base-domain>`）。

**4 种 deploy_mode 速查**（详尽：[deployer.md §2](generic-layer/deployer.md#2-4-种部署模式)）：

| 模式 | 啥时候用 |
|---|---|
| `dev-pod` | 单 PR 独立后端（如 APIMagic per-PR） |
| `data-pod` | 含 DB / cache / Vector（如 om-dataarts） |
| `shared` | 多 PR 共享后端（如 datastat 前端） |
| `none` | 工具仓 / 文档仓（如 om-deployment） |

**退出码**：0=就绪 / 2=入参错 / 3=apply 失败 / 4=readiness 超时 / 99=内部错。任一非 0 → orchestrate.sh 把 `pr-<N>.json` 的 `report` 字段直接传给 tester 作打回输入，本轮算失败。

**为啥不另起 k8s-deployer 跑**：流程 2 内 ai-dev-runner 已经有 KUBECONFIG 也持有当前 issue 上下文，少一跳。k8s-deployer 专给「不该把宽 K8s 权限给 ai-dev-runner」的项目用（旁支 PR preview workflow 用它）。runner 边界见 [runners.md §3.1](generic-layer/runners.md#31-角色)。

### 5.3 5 个 agent 的角色边界（对抗规则）

- **design**：只做设计，**不写代码**；定可量化验收标准
- **dev**：按 design 实现；**只改 `target_repos` 里的 dev 仓**，不碰 umbrella 自己的流水线代码
- **deploy**：纯脚本，4 种部署模式（dev-pod / data-pod / shared / none）见 [`generic-layer/deployer.md`](generic-layer/deployer.md)
- **tester**：4 类测试 — UT / 功能 / Playwright 场景 / 接口；按 design 验收标准逐条核
- **review**：先跑 4 项确定性门禁（敏感信息 / 漏洞 / License / 设计文档），再对抗式读 diff 挑 🔴/🟡 问题

通用 agent 设计说明：[`generic-layer/agents.md`](generic-layer/agents.md)
4 项门禁详尽：[`generic-layer/gates.md`](generic-layer/gates.md)
测试分层：[`generic-layer/tests.md`](generic-layer/tests.md) + [`testing-strategy.md`](testing-strategy.md)

### 5.4 收尾

- 回评 issue 2 条评论（部署完成 + 完整结果）：[`pr-comment-protocol.md`](pr-comment-protocol.md) §流程 2 评论模板
- 归档 `docs/change_logs/<date>-<source-repo>-issue-<N>.md`

### 5.5 用到的 secret

| Secret | 用途 |
|---|---|
| `OPENCODE_API_KEY` | 4 个 agent 调 LLM |
| `BACKLOG_REPO_TOKEN` / `CROSS_REPO_TOKEN` | 跨仓 clone / push / 开 PR |
| `AI_TEST_KUBECONFIG` | deployer 调 K8s 起预览 |
| `LOCAL_DB_PASSWORD` | APIMagic per-PR 模式建 PG 表 |

凭据档位完整清单：[`generic-layer/credentials-storage.md`](generic-layer/credentials-storage.md)

**完成判据**：issue 收到 2 条回评 + 每个 dev 仓有 head=`<BRANCH>` 的 open PR + 预览 URL 可访问。

**下一步**：人看预览 → 满意 → maintainer 评 `[<服务名>需求上线]`；不满意 → 再评 `[<服务名>需求实现]` 接着改（同分支增量）。

**详细**：[`stage-flow/flow-2-implementation.md`](stage-flow/flow-2-implementation.md)

---

## 6. 流程 3：`[<服务名>需求上线]` — 合入 + 上 beta + 清理

**触发**：maintainer 评 `[<服务名>需求上线]`（**仅白名单**；带 `[DRY_RUN]` 可干跑）。

**workflow 文件**：[`../projects/om-datacenter/.github/workflows/issue-3-merge-and-deploy.yml`](../projects/om-datacenter/.github/workflows/issue-3-merge-and-deploy.yml)
（runner：`self-hosted, ai-dev-runner`；timeout：25 min）

### 6.1 步骤

1. **权限校验**：触发评论的人必须在白名单（白名单写在 yml 的 step 0 里，不在仓里写死真实人名外的额外信息）。不在 → 评论拒绝原因 → 退出
2. **Checkout umbrella**：拉到 `src/deployer/deploy.py` 等流水线工具
3. **算 BRANCH + 找各 dev 仓 head=`<BRANCH>` open PR**：从 `.gitmodules` 枚举所有 submodule，对每个跑 `gh pr list --head $BRANCH --state open`
4. **门禁校验**：所有 PR 必须 `mergeable=MERGEABLE`（无冲突）
5. **逐 PR squash merge**：`gh pr merge --squash --delete-branch`
6. **逐仓 promote 到 beta**：调 `deploy.py promote --env beta`（触发 Jenkins job 上 beta；具体由 [`generic-layer/deployer.md`](generic-layer/deployer.md) §promote 段决定）
7. **逐 PR cleanup 预览**：调 `deploy.py cleanup --pr <N>` 删 namespace 内的预览 deployment / svc / ingress
8. **回评 issue**：贴上线结果 + 各仓 beta build 编号

**`[DRY_RUN]` 模式**：1-4 步照跑、5-7 步打印不执行，方便先验证。

### 6.2 用到的 secret

| Secret | 用途 |
|---|---|
| `BACKLOG_REPO_TOKEN` / `CROSS_REPO_TOKEN` | 跨仓 merge / 评论 |
| `AI_TEST_KUBECONFIG` | cleanup 预览 |
| `JENKINS_API_USER` / `JENKINS_API_TOKEN` | promote 到 beta 触发 Jenkins job |

**完成判据**：所有 PR 已 merge + 各仓 beta 已 rollout + 预览资源全部清理 + issue 收到结果回评。

**下一步**：beta 验证 → 生产发布（由项目独立的发布流程负责，不在本流水线范围）。

**详细**：[`stage-flow/flow-3-release.md`](stage-flow/flow-3-release.md) + [`release-process.md`](release-process.md)

---

## 7. 旁支：人工提 PR 的预览（不走需求流）

**触发**：项目 dev 仓 PR opened / synchronize / closed。

**workflow 文件**：[`../projects/om-datacenter/.github/workflows/pr-deploy-preview.yml`](../projects/om-datacenter/.github/workflows/pr-deploy-preview.yml)
（runner：`self-hosted, k8s-deployer`，**不是 ai-dev-runner**；见 [`generic-layer/runners.md`](generic-layer/runners.md) §k8s-deployer）

**步骤**：调 `deploy.py` 起预览 → 预览 URL 自动评论到 PR；PR closed → 触发 cleanup。

**详细**：[`stage-flow/flow-2-implementation.md`](stage-flow/flow-2-implementation.md) §旁支

---

## 8. 故障 / 回滚 / 复盘

- 上线异常 → [`release-process.md`](release-process.md) §回滚
- 复盘模板 → [`../teams/templates/Learn From the Incident/`](../teams/templates/Learn%20From%20the%20Incident/)
- 团队故障经验 → [`../teams/context/experience/`](../teams/context/experience/)

---

## 9. 关键约定速查

| 约定 | 值 | 文档 |
|---|---|---|
| Workflow runner 标签 | `self-hosted, ai-dev-runner` / `self-hosted, k8s-deployer` | [`generic-layer/runners.md`](generic-layer/runners.md) |
| 分支命名 | `<source-repo 短名>-issue-<N>` | [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md) |
| 预览 URL 格式 | `https://<repo-full-name>-<PR-number>.ai.test.osinfra.cn/` | [`generic-layer/deployer.md`](generic-layer/deployer.md) |
| 触发评论前缀 | `[<服务名>需求分析]` / `[<服务名>需求实现]` / `[<服务名>需求上线]` | 上文流程 1/2/3 |
| 报告归档目录 | `opensourceways/<repo>/issue_docs/<issueId>/<阶段>/` | [`stage-flow/flow-1-requirement.md`](stage-flow/flow-1-requirement.md) |
| 多 agent 对抗轮数 | `MAX_FIX_ROUNDS=3` | [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md) |
| Workflow 2 timeout | 90 min | [`generic-layer/workflow-skeletons.md`](generic-layer/workflow-skeletons.md) |
| 凭据存储档位 | GitHub Secret + K8s Secret + Vault sidecar | [`generic-layer/credentials-storage.md`](generic-layer/credentials-storage.md) |

---

## 10. 接下来

- 想接入新项目 → [`project-layer/onboarding-tier-B.md`](project-layer/onboarding-tier-B.md) 5 步走完
- 想看完整 om-datacenter 接入示例 → [`../projects/om-datacenter/`](../projects/om-datacenter/)
- 想理解 4 agent 怎么对抗 → [`generic-layer/orchestrator.md`](generic-layer/orchestrator.md) + [`generic-layer/agents.md`](generic-layer/agents.md)
- 想理解部署器 4 种模式 → [`generic-layer/deployer.md`](generic-layer/deployer.md)
- 想理解凭据怎么存 → [`generic-layer/credentials-storage.md`](generic-layer/credentials-storage.md)
- 想看 AI 辅助写需求的实际经验 → [`../teams/context/experience/AI辅助需求分析工作模式.md`](../teams/context/experience/AI%E8%BE%85%E5%8A%A9%E9%9C%80%E6%B1%82%E5%88%86%E6%9E%90%E5%B7%A5%E4%BD%9C%E6%A8%A1%E5%BC%8F.md)
