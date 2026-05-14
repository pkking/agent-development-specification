# Generic Layer — 测试编排

> 分层测试在流水线中的执行编排。代码：[`../../src/tests/`](../../src/tests/)。

## 1. 分层

详见 [`../../teams/standards/testing.md`](../../teams/standards/testing.md) 与 [`../testing-strategy.md`](../testing-strategy.md)。

| 层 | 跑哪 | 编排脚本 |
|---|---|---|
| smoke | ai-dev-runner 容器内 | `run_layered.sh smoke` |
| unit (UT) | 同上 | `run_layered.sh unit` |
| interface contract | 同上 | `run_layered.sh contract` |
| integration | 预览 namespace | `run_layered.sh integration` |
| e2e | 预览 namespace | `run_layered.sh e2e` |

## 2. run_layered.sh

入参 `<layer>` 决定要跑哪层；执行项目仓 `package.json` / `Makefile` / `pyproject.toml` 中对应 target，再聚合产出 JUnit XML + coverage report。

代码：[`../../src/tests/run_layered.sh`](../../src/tests/run_layered.sh)

## 3. 输出

- JUnit XML → 上传到 PR 评论
- 覆盖率报告 → 与 [`../../teams/security-gates/UT-coverage.md`](../../teams/security-gates/UT-coverage.md) 对照
- 失败用例 → 截图 / 日志归档到 PR artifacts

## 4. 项目层覆盖

项目可在 [`.preview/service.yaml`](../project-layer/preview-service-yaml-spec.md) 中声明 `test_targets`，覆盖默认的 `npm test` / `pytest`。

## 5. 关联

- 团队测试规范：[`../../teams/standards/testing.md`](../../teams/standards/testing.md)
- 测试经验：[`../../teams/context/experience/测试策略编写经验.md`](../../teams/context/experience/测试策略编写经验.md)
- tester agent prompt：[`../../teams/prompts/tester.md`](../../teams/prompts/tester.md)
