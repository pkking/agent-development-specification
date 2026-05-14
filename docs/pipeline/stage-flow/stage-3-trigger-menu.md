# 阶段 3 — 触发菜单

> 在已 accept 的 issue 上评论 `[<服务名>需求]`，机器人自动贴 3 流程触发菜单。

## 1. 谁触发

任意人（评论权限内）。

## 2. 做什么

```
人评 [<服务名>需求]
       ↓
caller workflow（项目仓） 接到 issue_comment
       ↓
机器人在 issue 上回评一条菜单：
  - 评 [<服务名>需求分析] 触发流程 1
  - 评 [<服务名>需求实现] 触发流程 2（流程 1 PR 合入后）
  - 评 [<服务名>需求上线] 触发流程 3（白名单）
```

## 3. 菜单 prompt

由项目层定义：`../../projects/<project>/prompts/trigger-menu.md`。
模板：[`../../projects/template/prompts/trigger-menu.md.tmpl`](../../projects/template/prompts/)。

## 4. 触发词命名

项目层 `<<TRIGGER_PREFIX>>` 占位符替换为实际值。如 om-datacenter 用「数据中台」/「小数」双触发。

## 5. 下一步

- 评 `[<服务名>需求分析]` → 进入流程 1

## 6. 关联

- 流程 1：[`flow-1-requirement.md`](flow-1-requirement.md)
- 项目层 caller workflow：[`../project-layer/caller-workflow-spec.md`](../project-layer/caller-workflow-spec.md)
