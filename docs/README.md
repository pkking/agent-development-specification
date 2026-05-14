# 基础设施服务团队 · 文档总入口

## 一句话

基础设施服务团队（数据中台 / 机器人服务 / 会议服务 / TTFHW / 社区数据采集 / ……）共用的
**「Issue → 需求分析 → AI 多 agent 对抗实现 → 预览 → 合入 → 上线」端到端自动化流水线**
+ 配套规范 + 项目接入模板 + 公共代码。

## 为什么有这个仓

| 价值 | 怎么实现的 |
|---|---|
| **零人工 CI/CD 编排** | 任何新项目按模板填占位符就有完整流水线，不写 CI yaml / 部署脚本 / 测试编排 |
| **统一规范** | 团队级规范（编码 / git / 测试 / 安全 / 发布）+ 项目级覆盖机制（项目可在自己仓里覆盖部分规范） |
| **质量门禁** | 4 项确定性检查（敏感信息 / 设计文档 / 漏洞 / License）+ 4 agent 多轮对抗 + 自动修复 |
| **预览环境** | 每个 PR 自动起独立 nginx Ingress 预览 URL，评审人直接看效果 |
| **AI 主导但人把关** | AI 写代码 / 写文档 / 跑测试 / 起预览，但每个阶段都需要人评论或合入触发，AI 不会自己往生产推 |

## 整体架构

```
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                          docs/  (本目录)                                 │
 │                                                                         │
 │   ┌──────────┐    ┌────────┐    ┌─────────────┐    ┌─────────────┐    │
 │   │ pipeline/│ ◄─ │ teams/ │ ◄─ │  projects/  │    │    src/     │    │
 │   │ 通用流水线 │ 引用 │ 团队规范 │ 引用 │ 项目接入模板 │    │ 公共代码     │    │
 │   │ + 全景图  │    │ + 模板  │    │ + 实例      │    │ + runner   │    │
 │   └──────────┘    └────────┘    └─────────────┘    └─────────────┘    │
 │         ▲                ▲                ▲                 ▲          │
 │         └────────────────┴────────────────┴─────────────────┘          │
 │              pipeline/architecture.md 全景图统一引用上述所有内容          │
 └─────────────────────────────────────────────────────────────────────────┘
```

## 工作流总览（高层）

```
[人] 在 backlog 仓提 issue
        ↓
[人] maintainer 评论 /accepts + 打 accepted 标签
        ↓
[人] 在 issue 评论  [<服务名>需求]   ───────► 机器人贴菜单
        ↓
[人] 在 issue 评论  [<服务名>需求分析] ───────► 流程 1：AI 写需求文档 → PR 到 backlog
        ↓ （需求 PR 合入后）
[人] 在 issue 评论  [<服务名>需求实现] ───────► 流程 2：4 个 AI agent 对抗实现 + 起预览
        ↓ （看预览满意）
[人] maintainer 评论 [<服务名>需求上线] ──────► 流程 3：合 PR + 上 beta + 清理预览
```

每一步具体怎么跑、用什么 prompt、什么 runner、什么 secret、什么脚本，**全在
[`pipeline/architecture.md`](pipeline/architecture.md)** 里 — 看一份就能搞懂全部。

## 4 大子目录

| 目录 | 做什么 | 谁会看 |
|---|---|---|
| **[`pipeline/`](pipeline/)** | 通用流水线完整文档（任何项目零认知），含全景图 + 通用机制详解 + 阶段流程 + 项目接线方法 | 想了解流水线机制；想接入新项目；想理解一次 issue 端到端怎么跑 |
| **[`teams/`](teams/)** | 团队级规范 + 5 类文档模板 + 公共 prompt + 安全门禁说明（被 pipeline 引用，不重写）| 写代码 / 提 PR / 写需求时查规范；改 prompt 参考 |
| **[`projects/`](projects/)** | 项目接入模板（`template/`）+ 实际项目实例（`om-datacenter/`）| 接入新项目按 `template/` 走；看 om-datacenter 怎么实际用 |
| **[`src/`](src/)** | 公共代码：2 类 runner（含 Dockerfile）+ 编排 + 部署器 + 门禁 + 测试 + 工具库 | 维护流水线代码；构建 runner 镜像；改部署逻辑 |

## 接入新项目 5 步

1. **复制模板**：`cp -r docs/projects/template/ docs/projects/<your-project>/`
2. **填占位符**：按 [`projects/template/ONBOARDING-CHECKLIST.md`](projects/template/ONBOARDING-CHECKLIST.md) 把 `<<PROJECT_NAME>>` 等占位符替换成实际值
3. **选档位**：A 档（仅 PR 预览）见 [`pipeline/project-layer/onboarding-tier-A.md`](pipeline/project-layer/onboarding-tier-A.md) / B 档（全 AI 开发）见 [`pipeline/project-layer/onboarding-tier-B.md`](pipeline/project-layer/onboarding-tier-B.md)
4. **项目仓配文件**：在你的项目仓加 caller workflow + `.preview/service.yaml` + `CLAUDE.md`，规范见 [`pipeline/project-layer/`](pipeline/project-layer/)
5. **自检**：跑 onboarding 自检脚本验证接入完整

## 快速开始（按角色）

| 我是谁 / 我想干嘛 | 看这里 |
|---|---|
| 我想了解流水线怎么跑 | [`pipeline/README.md`](pipeline/README.md) → [`pipeline/architecture.md`](pipeline/architecture.md) |
| 我想给我的项目接入这套自动化 | [`projects/template/README.md`](projects/template/README.md) |
| 我想知道 om-datacenter 怎么用 | [`projects/om-datacenter/README.md`](projects/om-datacenter/README.md) |
| 我想改 runner / 编排 / 部署器代码 | [`src/`](src/) 各子目录 README |
| 我想查团队规范 / 编码标准 | [`teams/standards/`](teams/standards/) |
| 我想查需求 / 架构 / 测试 / 发布文档模板 | [`teams/templates/`](teams/templates/) |
| 我想看 AI 辅助写需求 / 架构 / 测试的经验 | [`teams/context/experience/`](teams/context/experience/) |
| 我想看安全门禁怎么过 | [`teams/security-gates/`](teams/security-gates/) |

## 三层规范继承

```
个人层  ~/.claude/CLAUDE.md                  优先级最高，本机生效，可覆盖项目/团队规范
    ↑
项目层  projects/<project>/CLAUDE.md          项目专属规则，可覆盖团队规范
    ↑
团队层  teams/CLAUDE.md                       所有项目共用
```

详细规则见 [`teams/CLAUDE.md`](teams/CLAUDE.md) 第一段。

## 维护说明

- 本目录是**人主导编辑的文档与代码集合**，不自动生成
- 通用机制改动（pipeline/ + src/）需团队 review
- 项目实例（projects/`<project>`/）由各项目 owner 维护
- 团队规范（teams/）由团队 maintainer 提案 + 全员评审

## 关联

- 团队需求 / 文档归档相关规范 → [`teams/context/team/issue-workflow-guide.md`](teams/context/team/issue-workflow-guide.md)
- 数据中台项目实例 → [`projects/om-datacenter/`](projects/om-datacenter/)
- 团队规范主仓 → 本仓 `spec/` 和 `specification-example/`（平级目录）
