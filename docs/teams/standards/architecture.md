# 架构规范

## 1. 原则

- **单一职责**：一个服务一个领域；不允许「上帝服务」
- **数据所有权**：每张表只能被一个服务直接写；其他服务通过 API 访问
- **同步 vs 异步**：写多读少用同步 API；事件驱动用消息队列（不在跨域同步链路开 DB 事务）
- **依赖方向**：高层模块依赖抽象；具体实现注入

## 2. 设计文档

任何新服务 / 重大重构必须先有架构设计：

- 模板：[`../templates/Architecture Design/`](../templates/Architecture%20Design/)
- 写作经验：[`../context/experience/架构设计说明书编写经验.md`](../context/experience/架构设计说明书编写经验.md)
- AI 辅助：通过流水线 流程 1 自动生成草稿（[`../prompts/architecture-design.md`](../prompts/architecture-design.md)）

## 3. 评审

- 架构设计必须经至少 1 位团队 architect 评审通过
- 设计文档作为 PR 一部分合入；不允许「先做、后补文档」

## 4. 跨服务通信

- REST / gRPC 优先；契约用 OpenAPI / proto
- 异步用 Kafka / RabbitMQ；事件 schema 用 Avro / Protobuf
- 不允许直接读对方数据库

## 5. 部署

- 容器化（OCI）+ K8s 编排
- 部署模式 4 选 1：dev-pod / data-pod / shared / none，详见 [`../../pipeline/generic-layer/deployer.md`](../../pipeline/generic-layer/deployer.md)

## 6. 关联

- 流水线全景：[`../../pipeline/architecture.md`](../../pipeline/architecture.md)
- 安全设计：[`../context/team/安全设计与开发最佳实践.md`](../context/team/安全设计与开发最佳实践.md)
