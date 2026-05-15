# PR 评论协议

> 流水线在 PR / issue 上的评论遵循统一协议，保证机器可读 + 人可读。

## 1. 评论分类

| 类型     | 入口                            | 例                                         |
| -------- | ------------------------------- | ------------------------------------------ |
| 状态评论 | orchestrator / gates / deployer | 「smoke 通过」「预览 URL 已就绪」          |
| 反馈评论 | review / tester agent           | 「请补 UT」「契约不一致」                  |
| 触发回复 | 触发词识别                      | 「已派发 → 流程 2 启动」                   |
| 拒绝评论 | 白名单不过                      | 「评论人不在 maintainer 白名单，拒绝合入」 |

## 2. 格式

每条评论必含 5 段，详见 [`../teams/prompts/pr-comment.md`](../teams/prompts/pr-comment.md)：

```markdown
## <步骤名> — <成功 / 失败 / 警告>

**时间**：`<ISO8601 UTC>`
**触发**：`<触发源>`
**Run**：`<workflow run ID>`

### 摘要 ...

### 详情 ...

### 下一步 ...
```

## 3. 机器可读 marker

orchestrator 状态存到评论的特定 HTML 注释中：

```html
<!-- pipeline-state: { "round": 2, "stage": "review", "last_gate": "gates-passed" } -->
```

后续 workflow run 读取此评论解析 state，无需外部数据库。

## 4. 不允许

- 评论里贴完整日志（> 50 行）
- 贴 token / 内网域名 / 凭据
- 用 emoji 充字数

## 5. 关联

- 团队级 prompt：[`../teams/prompts/pr-comment.md`](../teams/prompts/pr-comment.md)
- 编排：[`generic-layer/orchestrator.md`](generic-layer/orchestrator.md)
