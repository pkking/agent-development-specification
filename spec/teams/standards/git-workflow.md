# Git 工作流规范

## 1. 分支模型

- `main` — 受保护，禁直接 push；合入只能通过 PR + 通过门禁
- `feature/<issue-id>-<short-desc>` — 单 issue 单分支
- `fix/<issue-id>-<short-desc>` — bug 修复
- `release/<version>` — 上线分支，仅 release manager 操作

## 2. Commit message

格式：`<type>: <subject>` —

| type       | 用途                |
| ---------- | ------------------- |
| `feat`     | 新功能              |
| `fix`      | bug 修复            |
| `docs`     | 仅文档              |
| `refactor` | 重构（无行为变化）  |
| `test`     | 测试相关            |
| `chore`    | 杂项（构建 / 工具） |

- 主题行 ≤ 70 字；不带句号
- 正文（可选）说明 **为什么**，不复述 diff
- 禁止 `Co-Authored-By: Claude...` 之类的 trailer（团队约定）

## 3. PR 流程

1. 从最新 `main` 起 `feature/...` 分支
2. 小步提交；commit 数 ≤ 10（多于此 squash）
3. 提 PR 后等流水线 4 项门禁通过
4. 经至少 1 个 reviewer approve 才能合
5. **不允许 AI 代 merge**；必须人点合按钮（项目级约束，见 `../../projects/<project>/CLAUDE.md`）

## 4. 禁止

- `git push --force` 到 `main` / 受保护分支
- `--no-verify` 跳 hook
- 直接 `git commit --amend` 已 push 出去的 commit
- 把敏感信息 push 出去后用 `--force` 抹掉（应轮换凭据 + 通知安全）

## 5. 关联

- 上线分支策略：[`release.md`](release.md)
- PR 评论 prompt：[`../prompts/pr-comment.md`](../prompts/pr-comment.md)
- 流水线 PR 评论协议：[`../../pipeline/pr-comment-protocol.md`](../../pipeline/pr-comment-protocol.md)
