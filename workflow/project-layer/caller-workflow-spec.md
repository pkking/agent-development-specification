# 项目层 caller-workflow 规范

> 项目仓 `.github/workflows/caller-workflow.yml` 是把 issue_comment 事件转给通用层的桥梁。

## 1. 职责

- 监听 issue_comment 事件
- 识别触发词 `[<服务名>需求...]`
- 通过 `repository_dispatch` 把事件转给通用层骨架仓

## 2. 必含

```yaml
on:
  issue_comment:
    types: [created]

jobs:
  dispatch:
    runs-on: ubuntu-latest
    if: github.event.issue.state == 'open'
    steps:
      - name: Parse trigger
        id: parse
        run: |
          # 识别 [<服务名>需求] / [<服务名>需求分析] / [<服务名>需求实现] / [<服务名>需求上线]
          # 设置 event_type 输出
      - name: Dispatch
        uses: peter-evans/repository-dispatch@v2
        with:
          token: ${{ secrets.DISPATCH_TOKEN }}
          repository: <generic-layer-org>/<generic-layer-repo>
          event-type: ${{ steps.parse.outputs.event_type }}
          client-payload: |
            {
              "issue_number": "...",
              "comment_author": "...",
              "project": "<<PROJECT_NAME>>"
            }
```

## 3. 触发词识别

| 评论                 | event_type            |
| -------------------- | --------------------- |
| `[<服务名>需求]`     | `trigger-menu`        |
| `[<服务名>需求分析]` | `requirement-analyze` |
| `[<服务名>需求实现]` | `implement-preview`   |
| `[<服务名>需求上线]` | `release-deploy`      |

## 4. 白名单校验

`release-deploy` 类型必须先在 caller workflow 里校验评论人在 maintainer 白名单内，
不在则直接评论拒绝原因 + 不 dispatch。

## 5. 模板

- 模板：[`../../projects/template/.github/workflows/caller-workflow.yml.tmpl`](../../projects/template/.github/workflows/)

## 6. 关联

- 通用层骨架：[`../generic-layer/workflow-skeletons.md`](../generic-layer/workflow-skeletons.md)
- 接入 B 档：[`onboarding-tier-B.md`](onboarding-tier-B.md)
- 触发菜单 prompt：项目层 `prompts/trigger-menu.md`
