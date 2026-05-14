# 接入自检清单

> 复制 `template/` 到 `<your-project>/` 后按本清单逐项替换 + 验收。

## A 档（仅 PR 预览） — 2 步

- [ ] 在项目仓加 `.github/workflows/pr-preview-caller.yml`（用本模板 [`.github/workflows/pr-preview-caller.yml.tmpl`](.github/workflows/pr-preview-caller.yml.tmpl)，替换 `<<PROJECT_NAME>>` 等占位符）
- [ ] 在项目仓加 `.preview/service.yaml`（用本模板 [`.preview/service.yaml.tmpl`](.preview/service.yaml.tmpl)，按需配 image / port / health check）

## B 档（全 AI 自动开发） — 5 步

完成上面 A 档 2 步基础上加：

- [ ] 在项目仓加 `CLAUDE.md`（用 [`CLAUDE.md.tmpl`](CLAUDE.md.tmpl)，**逐字填占位符 + 项目铁规**）
- [ ] 在项目仓加 `.github/workflows/caller-workflow.yml`（用 [`.github/workflows/caller-workflow.yml.tmpl`](.github/workflows/caller-workflow.yml.tmpl)，dispatch issue_comment 给通用层）
- [ ] 在项目仓加 `skills/`（可选；用 [`skills/skill-name.md.tmpl`](skills/skill-name.md.tmpl) 写项目自定义 skill）
- [ ] 在 docs/projects/`<your-project>`/prompts/ 填 4 个 prompt（trigger-menu / flow-1 / flow-2 / flow-3）
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
