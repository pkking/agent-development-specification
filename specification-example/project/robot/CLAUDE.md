# robot-tools — 机器人服务 AI 开发流水线工具仓

本仓是「机器人」服务接入 backlog 多服务 AI 流水线的**工具仓**（与
`opensourceways/om-datacenter` 对称：装通用 `src/orchestrate.sh` + `.github/agents/*`
+ `src/deployer/` + `src/gates/` + `src/tests/`，对项目零认知）。

`backlog/.github/workflows/implement.yml` 会 clone 本仓 + 按 `.gitmodules` 拉
**唯一 dev 仓 `community-robots`**，然后 `bash src/orchestrate.sh` 跑四 agent 对抗。

## dev 仓

| 子模块 | 角色 | 技术栈 | 基础分支 |
|--------|------|--------|---------|
| `community-robots` | 机器人接入服务（Gitee 机器人）| Go | `main` |

机器人是**单仓服务**——`target_repos` 只有 `community-robots` 或 `none`，没有 umbrella、没有多子仓联动。

---

## AI 自动开发流程（Workflow B / 四 agent 对抗）

> 逻辑在 `src/orchestrate.sh`，本节是「机器人」这个项目的接线（规则来源）。
> 四个 agent（`.github/agents/{design,dev,review,tester}.md`）开工前读本节。
> 机制通用：`orchestrate.sh` 用 `OM_TOOLS_DIR`/`OM_WORK_DIR` 参数化，dev 仓从
> `.gitmodules` 枚举（这里就是 `community-robots` 一个）。

### 触发与工作空间

- 触发：backlog issue 评论 `[机器人需求实现]`（由 `backlog/.github/workflows/implement.yml`
  在 `ai-develop-runner` 上跑；开工前从 backlog 仓拉已合入的《需求分析说明书》到
  `/tmp/opencode/requirement_analysis.md`，可能不存在则以 issue 内容为准）。
- 工作空间：`/workspaces/robot/<source 短名>-issue-<N>/`，里面 `git submodule update`
  出 `community-robots`。同一 issue 反复触发复用同目录。
- **分支命名**：dev 仓功能分支 = `<source-repo 短名>-issue-<N>`（如 `backlog-issue-389`）。

### 编排顺序（`src/orchestrate.sh`，每轮按序，最多 N 轮，N=`vars.GATE_FIX_ROUNDS` 默认 3）

```
① design  判路由 → 写 /tmp/opencode/route.json + design.md；mode=none 到此为止
② dev     按 design.md 改 community-robots 代码 → commit/push <branch> → 开 PR
          → 写 /tmp/opencode/result.json
③ deploy  调 src/deployer/deploy.py；community-robots 无预览注册 → deployer 按
          mode=none 跳过（机器人是后端 bot，本流程不强制起预览）
④ review  src/gates/run.sh（敏感/漏洞/License/设计文档 + 自动修）+ 对抗式 review diff
⑤ tester  UT（go test ./...）+ 按 design.md 验收标准核对 + src/tests/run_layered.sh
⑥ 失败且未到轮数上限 → 合成 feedback.md 回 ②；否则收尾回评 issue
```

### design：判路由规则

`target_repos` 只能是 `community-robots` 或 `none`。写 `/tmp/opencode/route.json`
（严格一行 JSON）：`{"mode":"normal|none","target_repos":["community-robots"],"add_community":null,"reason":""}`

**必须输出 `none` 的例外**（命中即 `mode=none`，不实施，回评正确处理路径）：
1. issue 实际在讲 `.github/` / workflow / CI、或 backlog/robot-tools 自身的脚本与元文件
2. 关于硬编码凭据 / token / kubeconfig 的安全告警类
3. `community-robots` 在 `/tmp/opencode/submodule_status.json` 的 `bad` 数组里
   （workflow 拉子模块失败）→ `mode=none`，reason 写「community-robots 子模块拉取
   失败（reason=…），无法实施，请运维确认 token/仓地址后重评」。**绝不**降级到别处
   hack 假装实现。
4. 看不出要改什么 → `none`，**绝不为了"至少改点"硬编**。

### 共享文件契约

- `/tmp/opencode/issue.txt`（fetch-issue 写）：issue 标题+正文+全部评论
- `/tmp/opencode/requirement_analysis.md`（可能不存在）：已合入的需求分析说明书
- `/tmp/opencode/route.json`（design 写，严格一行）：见上
- `/tmp/opencode/design.md`（design 写）：技术设计（具体文件/函数）+ 可量化验收标准 + 测试方案
- `/tmp/opencode/result.json`（dev 写，严格一行）：
  `{"mode":"...","target_repos":[...],"prs":[{"repo":"opensourceways/community-robots","number":NN}],"add_community":null,"reason":""}`；
  `mode=none`：`target_repos=[]`、`prs=[]`、填 `reason`
- `review_fail.md` / `test_fail.md` → orchestrate 合成 `/tmp/opencode/feedback.md` 回 dev；
  dev 只修清单问题、复用同 `$BRANCH`、不推翻已通过部分

### 机器人项目约定（dev/tester 必读）

- Go 项目：构建 `go build ./...`，单测 `go test ./...`，静态 `go vet ./...`
- 基础分支 `main`
- 不改 CI/部署元文件、不动凭据；只在 `community-robots` 内改业务代码
- **PR 只开不合**——合入永远是人的事；本流程也不直接 commit 到 community-robots 默认分支

---

## Commit 规范

- 禁止任何 AI 协作署名（`Co-Authored-By` / `Generated-By` / `with Claude` 等都不写）
- message 中文/英文均可，简明描述改动
