# tests/run_layered.sh — 分层测试入口

> 3 层测试: 冒烟(curl localhost) / vitest UT / 接口契约(PR diff 新增 endpoint 模拟调一遍).

## 命令

```
bash tests/run_layered.sh <PR_URL>
```

## 关联

- [`../../pipeline/generic-layer/tests.md`](../../pipeline/generic-layer/tests.md)
- [`../../pipeline/testing-strategy.md`](../../pipeline/testing-strategy.md)
