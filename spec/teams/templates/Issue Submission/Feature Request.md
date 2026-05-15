# Feature Request — 新增功能 / 体验改进

> 在 backlog 仓 New Issue 时选本模板。标题必须含 `[需求]`（这样流程 1 才走 ra-doc 模式自动写需求分析说明书 PR）。

## 标题格式

`[需求][<服务名>] <一句话需求场景>`

例：

- `[需求][数据中台] 新增 mindspore 社区采集与展示`
- `[需求][机器人] 给 op-bot 加上 /retest 重跑 CI 命令`

## 正文模板

```markdown
## 需求背景

<谁、在什么场景下、遇到什么问题；为什么之前没有这个功能，为什么现在需要>

## 需求详情

<具体要做什么；尽量列点描述输入 / 输出 / 用户能看到的变化>

## 预期价值

<上线后谁能受益、量化收益（人均节省 X 小时/月、QPS 提升 Y、新增覆盖 Z 个社区 等）>

## 涉及范围（建议，最终由 AI 流程 1 重新分析）

- [ ] 前端展示
- [ ] 后端 API
- [ ] 数据采集
- [ ] 部署 / 运维
- [ ] 其它：<填写>

## 相关参考

<已有的相关 issue / PR / 文档 / 截图 / 设计草图（可选）>
```

## 必含字段说明

| 字段     | 必填 | 说明                                                 |
| -------- | ---- | ---------------------------------------------------- |
| 需求背景 | ✓    | 不写背景的需求会被 maintainer 在 `/accepts` 阶段打回 |
| 需求详情 | ✓    | 至少 3 行描述；空 issue 直接关                       |
| 预期价值 | ✓    | 无量化数据时给定性描述 + 用户画像                    |
| 涉及范围 | 可选 | 给 AI 流程 1 路由参考；最终结论由 design agent 给    |
| 相关参考 | 可选 | 有图最好贴图，方便评审                               |

## 流程链接

- maintainer 评 `/accepts` 后进入阶段 2，详见 [`../../context/team/issue-workflow-guide.md`](../../context/team/issue-workflow-guide.md) §Stage 2
- 评 `[<服务名>需求分析]` → 流程 1（ra-doc 模式），详见 [`../../../pipeline/stage-flow/flow-1-requirement.md`](../../../pipeline/stage-flow/flow-1-requirement.md)

## 关联

- 同目录 Bug 模板：[`Bug Report.md`](Bug%20Report.md)
- 流程 1 用的 prompt：[`../../../projects/om-datacenter/.github/agents/requirements-doc.md`](../../../projects/om-datacenter/.github/agents/requirements-doc.md)
- 需求分析说明书（流程 1 产出物）模板：[`../Requirement Analysis/`](../Requirement%20Analysis/)
