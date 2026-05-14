#!/usr/bin/env bash
# 容器入口: 从环境变量读取 runner 注册信息 → 注册到 GitHub → 启动 runner
# 待填: 完整实现见 ../../pipeline/generic-layer/runners.md

set -euo pipefail
echo "[entrypoint] 待填: runner 注册逻辑"
exec /start-runner.sh
