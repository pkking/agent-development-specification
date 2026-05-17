# 变更发布流水线（release-mgmt）实现归档

> 这套「Issue → 变更计划 PR → 同意发布 → 通用发布流水线」已在 `opensourceways/release-mgmt`
> **真实端到端跑通验证**（自托管 runner + opencode 真生成 + 真扫描）。本目录是其
> 实现的**权威归档**（脚本/工作流/服务配置/runner 部署），供新服务接入与审计参考。
> 流程说明见 [`../../../workflow/change-release-process.md`](../../../workflow/change-release-process.md)。

## 目录结构

| 目录 | 内容 | 说明 |
|------|------|------|
| `workflows/` | `workflow_change.yml` / `release.yml` | 两条 GitHub Actions：变更计划生成 + 通用发布流水线 |
| `scripts/` | 11 个 Python | 确定性逻辑全脚本化（仅变更计划生成那步是 AI），可单测可复用 |
| `release-config/` | `<service>.yaml` | 通用流水线**配置驱动**：每服务一份，新增服务只加这一份 |
| `runner/` | runner manifest + 部署 README | 自托管 runner 部署（需集群 kubeconfig，运维一次性） |

## scripts/ 各脚本职责

| 脚本 | 职责 | 谁调 |
|------|------|------|
| `release_lib.py` | 共享库：命令执行 / gh api / 敏感扫描正则 / GITHUB_OUTPUT/ENV / issue 标题解析 | 全部 |
| `parse_issue.py` | 拉 Issue 标题/正文/评论 → issue.txt，解析服务/版本/repo@tag | workflow_change |
| `resolve_version.py` | **从源码仓现有 semver tag 自动推算 next 版本**（v1.0.0→v1.0.1，不采信 Issue 写的版本）| workflow_change / release |
| `svc_config.py` | 加载校验 `release-config/<service>.yaml`，输出配置驱动矩阵 | release |
| `verify_change_plan.py` | 变更计划产物存在性 + 敏感扫描（硬门禁） | workflow_change |
| `submit_change_plan.py` | git 分支/commit/push + 开/复用 PR | workflow_change |
| `comment_issue.py` | 各类 Issue 回评（成功/失败/发布完成/停止） | 两条 |
| `run_check.py` | 检查阶段单项**真扫**：secret/change-plan-integrity 硬门禁；sast(semgrep)/vuln(trivy,可配 vuln_block)/license/ut 运行时装工具真跑 | release |
| `prod_gate.py` | 生产准入：branch-check / image-vuln-scan(trivy) / virus-scan(clamav) | release |
| `build_image.py` | 真实构建：image.mode=local 走 containerd(nerdctl/buildah+ctr)，=swr 推华为云 SWR | release |
| `deploy_release.py` | 真实部署：deploy.mode none/kustomize/helm-value 改部署仓 | release |

## 已被真实运行验证（2026-05-17）

`opensourceways/release-mgmt` issue #10「发布 APIMagic 服务…」端到端真跑：
workflow_change（opencode 真生成 v1.0.1 变更计划→PR）→ 直提 main → 固定角色评 `同意发布`
→ release 全 12 job 绿（鉴权 / 版本推算 v1.0.1 / 6 项检查真扫 / 构建部署测试 / 生产准入 / 部署生产）。

真跑驱动修复并固化进上面脚本的 4 个真问题：版本自动推算、resolve 的 CONFIG_JSON 透传、
sast 对齐团队政策只卡 ERROR 级、vuln 按 `checks.vuln_block` 可配（默认严格拦 CRITICAL/HIGH，
书面风险接受后可降级）。详见 [`../../../workflow/change-release-process.md`](../../../workflow/change-release-process.md)。

## 凭据（全部走 env/secret，本目录脚本无任何硬编码密钥）

| 名称 | 用途 | 必需性 |
|------|------|--------|
| `RELEASE_MGMT_TOKEN` | 操作 release-mgmt（push/PR/评论）| 必需 |
| `OPENCODE_API_KEY` | workflow_change 跑 opencode 生成变更计划 | 必需 |
| `SOURCE_REPO_TOKEN` | clone/读私有源码仓 tag（与 RELEASE_MGMT_TOKEN 可不同）| 必需（私有源码仓）|
| `RELEASE_APPROVERS`(var) | 固定角色白名单（评 `同意发布` 才放行）| 必需 |
| `SWR_*` | 推华为云 SWR | 仅 image.mode=swr |
| `INFRA_COMMON_REPO_TOKEN` | 改部署仓 | 仅 deploy.mode≠none |
