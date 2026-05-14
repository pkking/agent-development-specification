# 数据中台 — 流程 2 项目化 Prompt

> 团队 prompt [`../../../teams/prompts/development.md`](../../../teams/prompts/development.md) 之后追加加载。

## 项目专属补充

- 子仓清单：`om-dataarts, om-dataarts-deployment, datastat-manage-website, om-deployment, APIMagic`
- 跨子仓改动：必须在 PR 描述列「同步改了哪些子仓 + 合入顺序」
- DB schema 改动：必须先在 `om-dataarts` 评审通过再改 `APIMagic`
- 前端文案：必须中英双语；硬编码中文文案必须配 i18n key

## 项目专属测试

- 元数据采集类改动 → 必须跑 `om-dataarts/test/regression/`
- API 契约改动 → 必须跑 `APIMagic/test/contract/` + datastat 前端 cypress

## 关联

- 团队 prompt：[`../../../teams/prompts/development.md`](../../../teams/prompts/development.md)
