# 数据中台 — 编码覆盖

> 与团队 [`../../../teams/standards/coding.md`](../../../teams/standards/coding.md) 的差异声明。

## 1. 与团队规范一致的部分

继承全部团队 coding.md 规则，不再重述。

## 2. 项目层差异

- **前端 (`datastat-manage-website`)**：行宽放宽到 120；文案必须中英双语，硬编码中文文案必须配 i18n key
- **API (`APIMagic`)**：handler 函数必须以 `handle_` 前缀；DB 查询必须经 dao 层不允许业务代码直接 ORM
- **采集任务 (`om-dataarts`)**：任务函数必须幂等，可重入；任务失败必须写入 `failed_tasks` 表而不是只打日志

## 3. 关联

- 团队编码规范：[`../../../teams/standards/coding.md`](../../../teams/standards/coding.md)
- 项目 CLAUDE：[`../CLAUDE.md`](../CLAUDE.md)
