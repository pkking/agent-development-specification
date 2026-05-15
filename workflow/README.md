# 通用流水线 (pipeline/)

> **本目录定义**：基础设施服务团队所有项目共用的「Issue → 发布」端到端自动化流水线的**通用方法论**。
> 任何基础设施项目（数据中台 / 机器人服务 / 会议服务 / TTFHW / ……）按本目录规范接入后，即可享受完整流水线。

---

## 从哪里看起

**第一份且唯一必读文档**：[`architecture.md`](architecture.md)

一份文档讲清楚：

- 每一阶段做什么（人做的 + AI 做的）
- 每一步用什么 prompt / 什么 runner / 什么 secret / 什么脚本 / 什么规范
- 每一步在什么目录跑、回显是什么、下一步是什么
- 所有细节均有可点击的下钻链接，单文档入口即可搞懂全部

读完 `architecture.md` 还要追细节就按下面的子目录看：

## 子目录导航

| 子目录                                             | 内容                                                                                                         | 什么时候看                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------ |
| [`generic-layer/`](generic-layer/)                 | **通用机制**（runner / deployer / orchestrator / agents / gates / tests / workflow 骨架 / credentials 规范） | 想理解流水线内部组件           |
| [`stage-flow/`](stage-flow/)                       | **端到端阶段**（issue 提交 / accept 门禁 / 菜单触发 / 3 个流程）                                             | 想理解人 + AI 在每个阶段做什么 |
| [`project-layer/`](project-layer/)                 | **项目接线方法**（A/B 档接入 / CLAUDE.md spec / skills spec / preview 规范 / caller workflow 规范）          | 想接入新项目                   |
| [`testing-strategy.md`](testing-strategy.md)       | 跨项目测试策略（UT / 功能 / 集成 / 前端 / 接口 / 其他服务）                                                  | 写测试 / 跑测试                |
| [`pr-comment-protocol.md`](pr-comment-protocol.md) | PR / issue 评论模板 + 调 gh CLI / API + token 配置                                                           | 自动评论怎么实现               |
| [`release-process.md`](release-process.md)         | 发布流程：白名单 / 灰度 / promote / cleanup / 回滚                                                           | 上线相关                       |

## 设计原则

1. **通用层 vs 项目层严格分离**：本目录的所有文档对项目零认知；项目专属逻辑都放在 `projects/<project>/`
2. **AI 主导但人把关**：每个阶段都需要人评论或合入触发，AI 不会自己往生产推
3. **失败可调试**：每一步 stdout 全部进 phase log，所有 commit 增量推
4. **质量门禁前置**：4 项确定性检查 + 4 agent 对抗，不依赖人工 review 兜底

## 关联

- 团队规范 / 文档模板 / 公共 prompt → [`../teams/`](../teams/)
- 新项目接入模板 → [`../projects/template/`](../projects/template/)
- 实际项目实例 → [`../projects/om-datacenter/`](../projects/om-datacenter/)
- 公共代码（runner 镜像 / 编排脚本 / 部署器 / 门禁 / 测试）→ [`../src/`](../src/)
