# Skill: add-community

> om-datacenter 项目自定义 skill。供 AI agent 在 issue 处理过程中识别 / 调用。

## 1. 名称

`om-datacenter-add-community`

## 2. 触发词

- 用户消息包含「新增社区」/「接入社区」/「加一个社区数据采集」
- issue 标题含 `[添加社区]` / `[新社区接入]`

## 3. 输入

| 字段             | 类型      | 必填 | 说明                                 |
| ---------------- | --------- | ---- | ------------------------------------ |
| `community_name` | string    | ✓    | 社区名（kebab-case），如 `mindspore` |
| `display_name`   | string    | ✓    | 展示名，如 `MindSpore`               |
| `repo_platform`  | enum      | ✓    | `github` / `gitee` / `gitcode`       |
| `repo_list`      | list[str] | ✓    | 接入的仓库清单                       |
| `meeting_source` | string    | 可选 | 会议数据源（如有）                   |

## 4. 步骤

1. 在 `om-dataarts` 仓 `communities/` 下加 `<community_name>.yaml`，按已有社区格式填写
2. 在 `APIMagic` 仓 `routes/communities.json` 注册新社区
3. 在 `datastat-manage-website` 加左侧导航条目 + 中英文案 i18n key
4. 跑 `om-dataarts/test/regression/test_community_<name>.py` 验证采集
5. 提 PR 跨 3 个子仓，按 [`../prompts/flow-2-implement.md`](../prompts/flow-2-implement.md) 项目铁规列同步合入策略

## 5. 输出

3 个 PR（每子仓一个）+ 1 条 issue 评论汇总链接。

## 6. 关联

- 团队 skill 规范：[`../../../pipeline/project-layer/skills-spec.md`](../../../pipeline/project-layer/skills-spec.md)
- 项目 CLAUDE：[`../CLAUDE.md`](../CLAUDE.md)
- 模板：[`../../template/skills/skill-name.md.tmpl`](../../template/skills/skill-name.md.tmpl)
