# gates/ — 4 项确定性门禁 + 自动修复

## 4 项门禁

1. 敏感信息扫描
2. 设计文档存在性
3. 漏洞扫描
4. License 合规

## 命令

```
bash gates/run.sh <PR_URL>
```

## 文件清单

- `run.sh` 主入口
- `checks.sh` 4 项检查
- `fixes.sh` 自动修复
- `lib.sh` 公共函数

## 关联

- [`../../pipeline/generic-layer/gates.md`](../../pipeline/generic-layer/gates.md)
- [`../../teams/standards/security.md`](../../teams/standards/security.md)
- [`../../teams/security-gates/`](../../teams/security-gates/)
