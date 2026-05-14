# 阶段 2 — 需求受理

> maintainer 在阶段 1 的 issue 上点 `/accepts`，正式认领该 issue。

## 1. 谁触发

项目 maintainer（白名单见项目 `projects/<project>/README.md` 的「白名单」段）。

## 2. 做什么

- 在 issue 评论 `/accepts`
- 机器人自动给 issue 打 `accepted` 标签
- 机器人自动指派 maintainer 为 issue 的 assignee

## 3. /accepts 协议

- 必须由 maintainer 评，他人评无效
- 评 `/accepts` 后才允许后续 `[<服务名>需求...]` 触发词生效
- 已 accept 的 issue 可被任意 maintainer 转交（再次评 `/accepts` 即自动重新指派）

## 4. 不允许

- 用户自己评 `/accepts`（机器人无视）
- 在 `accepted` 标签未打的 issue 上触发后续流程

## 5. 下一步

- 评 `[<服务名>需求]` → 进入阶段 3（机器人贴菜单）

## 6. 关联

- 团队 issue 工作流：[`../../teams/context/team/issue-workflow-guide.md`](../../teams/context/team/issue-workflow-guide.md)
- 阶段 3：[`stage-3-trigger-menu.md`](stage-3-trigger-menu.md)
