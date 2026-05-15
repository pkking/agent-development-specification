# 数据库规范

## 1. Schema

- 表名复数 + snake_case：`users`、`order_items`
- 主键统一 `id BIGINT`（或 UUID 字符串，项目层定）
- 必含三字段：`created_at`、`updated_at`、`deleted_at`（软删除）
- 外键必须显式声明且加索引；不接受「应用层维护引用」

## 2. 迁移

- 用 Flyway / Liquibase / Alembic / Prisma migrate（项目层选一）
- 迁移脚本**只增不删**；删字段要分两次发版（先停写、后真删）
- 大表 DDL 必须 review + 在备库验证 + 选低峰窗口
- 上线前在预览环境（dev / preview namespace）跑通

## 3. 查询

- 禁止 `SELECT *`；显式列字段
- 禁止字符串拼 SQL；用 ORM 或参数化
- N+1 查询：必须在 PR review 中识别并修
- 慢查询 > 200 ms 必须打到慢查询日志 + 加索引

## 4. 事务

- 跨服务不开分布式事务；用 outbox + 幂等消费
- 长事务（> 1 s）禁；拆批

## 5. 备份与恢复

- 项目层在 `docs/deployment.md` 写明 RPO / RTO 与恢复演练频率

## 6. 关联

- 安全：[`security.md`](security.md)
- 可观测性（慢查询告警）：[`observability.md`](observability.md)
