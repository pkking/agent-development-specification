# 项目接入 — A 档（仅 PR 预览）

> 最轻量接入，2 步完成，仅获得 PR 自动起预览的能力，不带 AI 多 agent 开发。

## 适用

- 已有较成熟的 dev 工作流，只想要「PR → 预览 URL」自动化
- 不需要 AI 写需求 / 架构 / 代码
- 不需要 issue 触发的多流程

## 步骤

### 第 1 步：caller workflow

在项目仓加 `.github/workflows/pr-preview-caller.yml`：

- 模板：[`../../projects/template/.github/workflows/pr-preview-caller.yml.tmpl`](../../projects/template/.github/workflows/)
- 替换占位符：`<<PROJECT_NAME>>`、`<<NAMESPACE>>`、`<<BASE_DOMAIN>>`

### 第 2 步：service.yaml

在项目仓加 `.preview/service.yaml`：

- 模板：[`../../projects/template/.preview/service.yaml.tmpl`](../../projects/template/.preview/)
- 配 `deploy_mode`（dev-pod / data-pod / shared / none）
- 配 image / port / health check

## 验收

- 提一个测试 PR
- 看 ai-dev-runner / k8s-deployer 跑通
- PR 评论出现预览 URL，可访问

## 关联

- 完整模板：[`../../projects/template/`](../../projects/template/)
- 自检清单：[`../../projects/template/ONBOARDING-CHECKLIST.md`](../../projects/template/ONBOARDING-CHECKLIST.md)
- 部署模式说明：[`../generic-layer/deployer.md`](../generic-layer/deployer.md)
- B 档（全 AI 开发）：[`onboarding-tier-B.md`](onboarding-tier-B.md)
