# 变更发布流程（release-mgmt 治理）

> 这是流程 3「合入 + 上 beta」之后、**生产发布的治理层**。生产发布不再是"release manager 拍脑袋手动触发"，而是收敛到 **`release-mgmt` 仓**：以 Issue 为单位，先自动生成《变更计划说明书》并评审合入，再由固定角色评论 `同意发布` 触发带多重硬门禁的发布流水线。
>
> 与 [`release-process.md`](release-process.md)（流程 3 之后的总体发布过程）、团队层 [`../spec/teams/standards/release.md`](../spec/teams/standards/release.md) 相辅相成；本文件聚焦 release-mgmt 这一治理闭环。

## 0. 已真实验证（2026-05-17，权威实现归档）

本闭环已在 `opensourceways/release-mgmt`（issue #10）**端到端真实跑通**：自托管 runner
真注册、opencode 真生成变更计划、semgrep/trivy/license 真扫、release 全 12 job 绿。
实现（脚本/工作流/服务配置/runner 部署）权威归档在
[`../spec/teams/release-pipeline/`](../spec/teams/release-pipeline/README.md)。

**真跑校准后的真实逻辑要点（务必按这些理解，不是设计想象）：**

1. **版本号自动推算，不采信 Issue 写的版本**：`resolve_version.py` 查源码仓现有
   semver tag，取最新 patch+1（如 APIMagic 已有 `v1.0.0` → 本次发 **`v1.0.1`**；
   无 tag 才 `v0.0.1`）。Issue 标题/正文写错或不写版本都不影响——以源码仓 tag 为准。
2. **确定性步骤全脚本化**：除「opencode 生成变更计划」这一步是 AI，解析/校验/敏感扫描/
   git/PR/回评/版本推算/配置加载/各检查/构建/部署全是 `scripts/*.py`，可单测可复用，
   不依赖 AI 输出格式。
3. **检查项真扫，不再 dry 跳过**：sast=semgrep（只卡 **ERROR 级**，对齐团队门禁政策，
   WARNING/INFO 不挡）、vuln=trivy fs（CRITICAL/HIGH）、license=license-checker、
   ut。runner 缺工具时**运行时自动安装**（semgrep 用 pip、trivy 下静态二进制），
   实在装不上才 SKIP（只读检查不挡，与服务侧 CI 互补）。secret-scan /
   change-plan-integrity 始终硬门禁。
4. **漏洞门禁可按服务配 + 书面风险接受**：`checks.vuln_block` 默认 `true`（发现
   CRITICAL/HIGH 即阻断，**默认严格不削弱**）；服务在变更计划书面记录风险接受后，
   可在 `release-config/<svc>.yaml` 设 `false` 降为告警不阻断（真实发布治理惯例）。
5. **演练 vs 正式**：`同意发布`=演练（不真推镜像/不真改部署仓，但**检查项照样真扫**）；
   `同意发布 正式`=正式。**容器构建**：`image.mode=local` 正式态需 runner 具备
   containerd 链（nerdctl 或 buildah+ctr + 挂 `/run/containerd/containerd.sock`），
   缺则 `build_image.py` 明确报错指明运维补什么（不静默假成功）；演练态不触发真构建。
6. **私有源码仓**：`SOURCE_REPO_TOKEN`（能 clone/读私有源码仓 tag 的 PAT，可与
   `RELEASE_MGMT_TOKEN` 不同）；缺失则版本推算与源码扫描会明确失败并提示。

## 1. 全景

```
在 release-mgmt 仓提「发布/变更/版本」类 Issue
        │  例："发布 APIMagic 服务 v1.0.0 到今天的变更发布"（服务名任意）
        ▼  workflow_change（自托管 runner）
  按 ai-release-plan Skill 跑 AI：仓库@tag 自动 diff 发现关联 Issue/PR
  → 生成《变更计划说明书》issue_docs/<N>/Release/#<N> ... .md
  → 提 PR（resolve #N）→ 回评 Issue
        │
        ▼  人评审 / 补充 → 合入变更计划 PR（merge 永远是人的事）
        │
        ▼  固定角色在该 Issue 评论 `同意发布`（或 `同意发布 正式`）
        ▼  release（自托管 runner，多检查项 fail-fast）
  ① 角色鉴权（白名单 vars.RELEASE_APPROVERS）
  ② 变更计划存在性硬门禁（issue_docs/<N>/Release/*.md 必须已在 main）
  ③ 6 项检查（含敏感扫描 / 执行步骤+回滚方案完整性 …）
  ④ 构建并部署测试环境
  ⑤ 3 项生产准入（镜像漏洞 / 病毒 / 发布分支）
  ⑥ 部署生产 → ArgoCD 同步
  —— 任一检查项失败立即停止后续并回评 Issue
```

## 2. 两条 workflow

| workflow | 触发 | 跑在哪 | 职责 |
| -------- | ---- | ------ | ---- |
| **workflow_change** | release-mgmt 仓 Issue `opened`（标题含 发布/变更/版本）；或评论 `[重新生成变更计划]` | `self-hosted, ai-dev-runner`（复用发布 runner，非 GitHub 托管） | 按 [`../spec/teams/prompts/ai-release-plan.md`](../spec/teams/prompts/ai-release-plan.md) 用 AI 生成《变更计划说明书》→ 提 PR → 回评 |
| **release** | 该 Issue 下评论 `同意发布`（演练）/ `同意发布 正式`（正式） | `self-hosted, ai-dev-runner` | 鉴权 → 变更计划存在性硬门禁 → 多检查项串行 → 构建/部署测试 → 生产准入 → 部署生产；fail-fast |

> Runner 标签与既有流水线一致，见 [`generic-layer/runners.md`](generic-layer/runners.md)。两条均**不用 GitHub 托管 runner**。

## 3. 角色与触发约定

| 项 | 约定 |
| -- | ---- |
| 谁能触发发布 | 仓库变量 `vars.RELEASE_APPROVERS`（逗号分隔 GitHub 登录名）里的**固定角色**；精确匹配，不在白名单 → 拒绝并回评、流水线停止 |
| 演练 vs 正式 | `同意发布` → dry_run（不真推镜像 / 不真改部署仓，只验证全链路）；`同意发布 正式` / `同意发布 --prod` → 正式发布 |
| 服务名 | 从 Issue 标题自动解析（"发布 \<服务\> ..." / "\<服务\> vX.Y.Z ..."），与具体服务解耦 |
| 变更计划缺失 | release 流水线第 ② 步硬门禁：`issue_docs/<N>/Release/*.md` 不在 main → 立即停止并回评（必须先合入变更计划 PR） |
| merge | 变更计划 PR 的合入**永远由人完成**，workflow 不自动 merge |

## 4. 变更计划说明书

- **模板**（权威结构，严格遵循）：[`../spec/teams/templates/Release/#1 Release Specification.md`](../spec/teams/templates/Release/%231%20Release%20Specification.md)
- **生成 Skill**：[`../spec/teams/prompts/ai-release-plan.md`](../spec/teams/prompts/ai-release-plan.md)
- **编写经验**：[`../spec/teams/context/experience/变更计划编写经验.md`](../spec/teams/context/experience/%E5%8F%98%E6%9B%B4%E8%AE%A1%E5%88%92%E7%BC%96%E5%86%99%E7%BB%8F%E9%AA%8C.md)
- 归档位置：release-mgmt 仓 `issue_docs/{issueId}/Release/`，issueId = release-mgmt Issue 编号
- 核心内容：变更概览（关联 Issue/PR 汇总、变更等级 L1/L2/L3）、详细执行步骤、生产环境验证、回滚方案

## 5. 多检查项 fail-fast

release 流水线把检查项拆成独立 job，GitHub Actions `needs` 默认仅在依赖成功时运行，因此**任一检查项失败 → 下游全部跳过 → 流水线停止**，并由 `on_failure` 兜底回评 Issue。检查项分两组：

- **检查阶段（6 项并行）**：敏感信息扫描、变更计划完整性（执行步骤+回滚方案必须存在）、SAST / 漏洞 / License / UT（服务侧 CI 已保证，发布流水线按需扩展）
- **生产准入（3 项并行）**：镜像漏洞扫描、病毒扫描、发布分支校验

任一组内 `fail-fast: true`，组间靠 `needs` 串联。检查口径对齐安全门禁规范，见 [`generic-layer/gates.md`](generic-layer/gates.md) 与 [`../spec/teams/security-gates/`](../spec/teams/security-gates/)。

## 6. 与流程 3 的衔接

| 阶段 | 由谁负责 | 文档 |
| ---- | -------- | ---- |
| 合入实现 PR + 上 beta | 流水线流程 3 | [`stage-flow/flow-3-release.md`](stage-flow/flow-3-release.md) |
| beta 值守 / 灰度策略 | 团队发布规范 | [`../spec/teams/standards/release.md`](../spec/teams/standards/release.md) |
| **生产发布治理（本文件）** | release-mgmt：变更计划 + 同意发布门禁 | 本文件 |
| 故障 / 回滚 / 复盘 | — | [`release-process.md`](release-process.md) §回滚、[`../spec/teams/templates/Learn From the Incident/`](../spec/teams/templates/Learn%20From%20the%20Incident/) |

## 7. 失败处理

| 失败点 | 行为 |
| ------ | ---- |
| 变更计划未生成（AI 输出空 / 命中敏感） | workflow_change fail，回评 Issue 提示 `[重新生成变更计划]` 重试 |
| 评论人不在白名单 | release 鉴权 job fail，回评拒绝原因，不执行任何发布动作 |
| 变更计划不在 main | release 第 ② 步 fail，回评"先合入变更计划 PR" |
| 任一检查/准入项失败 | 下游 job 跳过，`on_failure` 回评"某检查项失败，已停止"，修复后重评 `同意发布` 重跑 |

## 8. 关联

- 流程 3（合入 + 上 beta）：[`stage-flow/flow-3-release.md`](stage-flow/flow-3-release.md)
- 总体发布过程：[`release-process.md`](release-process.md)
- 团队发布规范：[`../spec/teams/standards/release.md`](../spec/teams/standards/release.md)
- 变更计划模板 / Skill / 经验：见 §4
- Runner：[`generic-layer/runners.md`](generic-layer/runners.md)
- 安全门禁：[`generic-layer/gates.md`](generic-layer/gates.md)
