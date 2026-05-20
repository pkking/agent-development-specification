# 机器人服务（robot）接入示例

> 这是「机器人」服务接入 backlog 多服务 AI 流水线的**实况示例**（与
> `specification-example/project/om-datacenter/` 对称）。**robot 独有的细节都在这里**，
> 总文档 [`workflow/architecture.md`](../../../workflow/architecture.md) 只引用本目录，
> 不把 robot 专属内容塞进通用架构文。

## 1. 接入拓扑（robot 独有）

```
backlog 仓（多服务统一入口，通用 workflow + 配置，不动通用层）
  ├─ .github/services/robot.yaml      服务注册表（analyze + implement 已接通）
  │     analyze   handler=in-repo  触发 [机器人需求分析]
  │     implement handler=in-repo  触发 [机器人需求实现]
  │     release   disabled（后续开放）
  │     implement.tools_repo = opensourceways/robot-tools
  └─ .github/workflows/{analyze-requirement,implement,auto-analyze-on-accept}.yml（通用，零改）
        │
        ▼ implement.yml clone tools_repo + 其 .gitmodules 子仓
opensourceways/robot-tools（工具仓，与 opensourceways/om-datacenter 对称）
  ├─ src/{orchestrate.sh,deployer,gates,tests}   通用，对项目零认知
  ├─ .github/agents/{design,dev,review,tester}.md 通用对抗 agent
  ├─ CLAUDE.md                                   robot「AI 自动开发流程」（见本目录 CLAUDE.md）
  └─ .gitmodules → opensourceways/community-robots（**唯一 dev 仓**，单仓 Go 服务，未归档活跃）
```

- 服务注册表样例：[`spec/teams/external-workflows/services-examples/robot.yaml`](../../../spec/teams/external-workflows/services-examples/robot.yaml)
- 工具仓的 robot「AI 自动开发流程」：本目录 [`CLAUDE.md`](CLAUDE.md)

## 2. 与 datacenter 的差异（robot 独有点）

| 维度           | datacenter                      | robot                                        |
| -------------- | ------------------------------- | -------------------------------------------- |
| 工具仓         | `opensourceways/om-datacenter`  | `opensourceways/robot-tools`                 |
| dev 仓         | 5 个 submodule（umbrella）      | **单仓** `opensourceways/community-robots`   |
| `target_repos` | apimagic/datastat/om-dataarts/… | 只有 `community-robots` 或 `none`            |
| 基础分支       | 各仓不一                        | `main`                                       |
| 预览           | 起 dev-pod 预览                 | 后端 bot，无预览注册 → deployer 按 none 跳过 |
| release        | forward 到 om-datacenter        | 暂 disabled                                  |

## 3. 已真实端到端验证（2026-05-18）

| 环节                                          | 真实结果                                                                                                                                      |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| AI-native 模板 → accepted 自动起分析          | backlog #389/#393 两次验证：打 `accepted` → `auto-analyze-on-accept` 自动贴 `[机器人需求分析]` → 需求分析真跑回评（无需人工评触发词）         |
| 归档仓护栏                                    | dev 仓最初误用已归档的 `robot-gitee-access` 时，dev agent **正确判 mode=none 拒绝伪造**（归档仓不能开 PR），按设计护栏生效                    |
| 切到 `community-robots` 后 `[机器人需求实现]` | implement.yml run **success** → orchestrate 四 agent 对抗一轮全过 → dev **真开 PR `opensourceways/community-robots#2`（open，未合，未直提）** |

结论：机器人「需求分析 + 需求开发」**全链路真实跑通**；护栏（归档仓拒绝、PR 只开不合）按设计正确生效。

## 4. 新增一个类似单仓服务怎么做（通用方法，robot 即范例）

1. 建工具仓 `<org>/<svc>-tools`：拷通用 `src/` + `.github/agents/` + 写 `.gitmodules`→该服务 dev 仓 + 写本目录这种 `CLAUDE.md`（单仓「AI 自动开发流程」，`target_repos` 只列该 dev 仓或 none）
2. backlog 加 `.github/services/<svc>.yaml`：`analyze`/`implement` `handler: in-repo` + 触发词 + `implement:` 段 `tools_repo` 指向上面工具仓
3. 组织通用 issue 模板的「目标服务」下拉加该服务（可选，享 accepted 自动起分析）
4. 通用 workflow / 脚本 / runner **一律不改**

> dev 仓必须**未归档**（归档仓不能推分支/开 PR，护栏会直接 mode=none 拒绝）。
