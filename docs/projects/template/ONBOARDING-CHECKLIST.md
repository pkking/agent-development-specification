# 接入自检清单

> 复制 `template/` 到 `<your-project>/` 后按本清单逐项替换 + 验收。

## A 档（仅 PR 预览） — 2 步

- [ ] 在项目仓加 `.github/workflows/pr-preview-caller.yml`（用本模板 [`.github/workflows/pr-preview-caller.yml.tmpl`](.github/workflows/pr-preview-caller.yml.tmpl)，替换 `<<PROJECT_NAME>>` 等占位符）
- [ ] 在项目仓加 `.preview/service.yaml`（用本模板 [`.preview/service.yaml.tmpl`](.preview/service.yaml.tmpl)，按需配 image / port / health check）

## B 档（全 AI 自动开发） — 5 步

完成上面 A 档 2 步基础上加：

- [ ] 在项目 umbrella 仓加 `CLAUDE.md`（用 [`CLAUDE.md.tmpl`](CLAUDE.md.tmpl)，**逐字填占位符 + 项目铁规**）
- [ ] 在项目**来源仓**（如 backlog）加 `.github/workflows/caller-workflow.yml`（用 [`.github/workflows/caller-workflow.yml.tmpl`](.github/workflows/caller-workflow.yml.tmpl)，dispatch issue_comment 给通用层）
- [ ] 在项目 umbrella 仓加 **3 个 workflow yml**（每个 .tmpl 都要替换占位符）：
  - [ ] `.github/workflows/issue-1-analyze-requirement.yml`（用 [`.github/workflows/issue-1-analyze-requirement.yml.tmpl`](.github/workflows/issue-1-analyze-requirement.yml.tmpl)）
  - [ ] `.github/workflows/issue-2-implement-and-preview.yml`（用 [`.github/workflows/issue-2-implement-and-preview.yml.tmpl`](.github/workflows/issue-2-implement-and-preview.yml.tmpl)）
  - [ ] `.github/workflows/issue-3-merge-and-deploy.yml`（用 [`.github/workflows/issue-3-merge-and-deploy.yml.tmpl`](.github/workflows/issue-3-merge-and-deploy.yml.tmpl)）
  - [ ] `.github/workflows/pr-deploy-preview.yml`（用 [`.github/workflows/pr-deploy-preview.yml.tmpl`](.github/workflows/pr-deploy-preview.yml.tmpl)；旁支 PR 预览）
  - 3+1 个 yml 的拓扑和占位符索引：[`.github/workflows/README.md`](.github/workflows/README.md)
- [ ] 在项目 umbrella 仓加 `.github/agents/`（含 requirements-doc / design / dev / review / tester 5 个 agent prompt，可拷 [`../om-datacenter/.github/agents/`](../om-datacenter/.github/agents/) 改）
- [ ] 在项目 umbrella 仓加 `skills/`（可选；用 [`skills/skill-name.md.tmpl`](skills/skill-name.md.tmpl) 写项目自定义 skill）
- [ ] 在 docs/projects/`<your-project>`/prompts/ 填 4 个项目层 prompt（trigger-menu / flow-1 / flow-2 / flow-3）
- [ ] 在 docs/projects/`<your-project>`/docs/ 填 6 个项目文档（architecture / coding-overrides / test-strategy / api-spec / deployment / credentials-inventory）

## 验收（提交前最后跑一次）

- [ ] 在项目仓提一个测试 issue（标题 `[需求] 接入自检测试`）
- [ ] maintainer 评 `/accepts`
- [ ] 评论 `[<TRIGGER_PREFIX>需求]` → 菜单评论出现
- [ ] 评论 `[<TRIGGER_PREFIX>需求分析]` → 流程 1 跑通，需求文档 PR 出现在 backlog 仓
- [ ] 评论 `[<TRIGGER_PREFIX>需求实现]` → 流程 2 跑通，dev 仓出现 PR + 预览 URL 可访问
- [ ] 评论 `[<TRIGGER_PREFIX>需求上线] [DRY_RUN]` → 流程 3 dry-run 通过

## 凭据补全

按 [`docs/credentials-inventory.md.tmpl`](docs/credentials-inventory.md.tmpl) 列出本项目用到的 secret，在 GitHub repo / org settings 加齐。

参考：[`../../pipeline/generic-layer/credentials-storage.md`](../../pipeline/generic-layer/credentials-storage.md)
