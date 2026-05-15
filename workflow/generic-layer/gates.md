# Generic Layer — 4 项确定性门禁

> PR 进入 review 前必跑、必过的 4 项机器检查。代码：[`../../src/gates/`](../../src/gates/)。

## 1. 4 项门禁

| 门禁 | 工具 | 失败行为 |
|---|---|---|
| 敏感信息检测 | gitleaks（详见 [`../../teams/security-gates/Gitleaks.md`](../../teams/security-gates/Gitleaks.md)） | 评论标记 → orchestrator 进入修复轮 |
| 设计文档检测 | 自研 `docs-check`（要求 PR 含 `docs/architecture.md` 或 `docs/api-spec.md` 改动） | 同上 |
| 漏洞扫描 | SAST（详见 [`../../teams/security-gates/SAST.md`](../../teams/security-gates/SAST.md)） | 同上 |
| License 合规 | `licenses-check`（黑白名单见 [`../../src/gates/lib.sh`](../../src/gates/lib.sh)） | 同上 |

## 2. 单 PR 执行

```
gates/run.sh
   ├─ gates/checks.sh     ← 跑 4 项检查
   ├─ gates/fixes.sh      ← 自动修能修的（License header / 简单 SAST 提示）
   └─ gates/lib.sh        ← 公共工具
```

## 3. 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 全过，可进 review |
| 10 | 敏感信息检测失败 |
| 20 | 设计文档缺失 |
| 30 | 漏洞检测失败 |
| 40 | License 不合规 |
| 99 | 内部错误 |

## 4. 与 4 agent 协同

orchestrator 在每轮 dev → review 之间夹一次 gates；
失败的退出码 + 详情写入 PR 评论，dev agent 在下一轮读到并修复。

## 5. 项目层定制

项目可在 `projects/<project>/docs/security.md` 中声明额外门禁（如 K8s policy check、IaC 合规扫描），通过 [`.preview/service.yaml`](../project-layer/preview-service-yaml-spec.md) 的 `extra_gates` 字段注入。

## 6. 关联

- UT 覆盖率门禁单独走：[`../../teams/security-gates/UT-coverage.md`](../../teams/security-gates/UT-coverage.md)
- 编排：[`orchestrator.md`](orchestrator.md)
- 团队级安全规范：[`../../teams/standards/security.md`](../../teams/standards/security.md)
