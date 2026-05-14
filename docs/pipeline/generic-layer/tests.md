# Tests — 分层测试机制

> 本文件描述分层测试 `tests/run_layered.sh` 三层：冒烟（curl localhost）/ vitest UT / 接口契约（PR diff 新增 endpoint 模拟调一遍）+ tester agent 跑 Playwright 场景。

## 1. 概述

待填：本文件描述的组件 / 机制是什么，在 [`../architecture.md`](../architecture.md) 哪一步用到。

## 2. 详细设计

待填：组件结构 / 内部交互 / 配置 / 失败模式。

## 3. 关联文档

- 全景图：[`../architecture.md`](../architecture.md)
- 项目接线规范：[`../project-layer/`](../project-layer/)
- 公共代码：[`../../src/`](../../src/)
