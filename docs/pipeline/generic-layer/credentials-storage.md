# Credentials Storage — 凭据存储与注入规范

> 本文件描述凭据的三层存储：GitHub repo Secret（CI 凭据）/ K8s Secret（运行时凭据）/ Vault sidecar（应用配置含密码），以及在 workflow / Pod / 应用层各自的注入方式与轮转规范。

## 1. 概述

待填：本文件描述的组件 / 机制是什么，在 [`../architecture.md`](../architecture.md) 哪一步用到。

## 2. 详细设计

待填：组件结构 / 内部交互 / 配置 / 失败模式。

## 3. 关联文档

- 全景图：[`../architecture.md`](../architecture.md)
- 项目接线规范：[`../project-layer/`](../project-layer/)
- 公共代码：[`../../src/`](../../src/)
