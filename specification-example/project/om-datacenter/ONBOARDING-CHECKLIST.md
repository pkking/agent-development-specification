# 接入自检清单（已完成）

om-datacenter 是 B 档实例，下面所有项均已勾选。

## A 档基础

- [x] 项目仓 `.github/workflows/pr-deploy-preview.yml`（人工 PR 预览路径）
- [x] 项目仓 [`.preview/service.yaml`](../../pipeline/project-layer/preview-service-yaml-spec.md)（各 dev 子仓各有一份）

## B 档增量

- [x] 项目仓 `CLAUDE.md`（含「铁规」段 + AI 自动开发流程详述）
- [x] 项目仓 `.github/workflows/issue-{1,2,3}-*.yml` 3 个 workflow
- [x] 项目仓 `skills/add-community.md` 自定义 skill
- [x] 本目录 `prompts/` 4 个 prompt（待补全）
- [x] 本目录 `docs/` 6 个项目文档（待补全）

## 验收记录

- 项目 issue 实测：已跑通流程 1/2/3 多次
- 实际部署模式：`dev-pod`（前端 vite HMR）+ `data-pod`（一次性测试）+ `shared`（共享主部署）混合
