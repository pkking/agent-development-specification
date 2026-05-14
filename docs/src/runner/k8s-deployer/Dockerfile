# K8s 部署 runner runner 镜像
# 待填: from 基础镜像 + 装 opencode / git / node / java / maven / python / kubectl + 加 entrypoint

FROM ubuntu:24.04

# 待填: 装包
# RUN apt-get update && apt-get install -y ...

# 待填: 装 opencode CLI
# 待填: 装 kubectl

COPY entrypoint.sh /entrypoint.sh
COPY start-runner.sh /start-runner.sh
RUN chmod +x /entrypoint.sh /start-runner.sh

WORKDIR /home/runner
ENTRYPOINT ["/entrypoint.sh"]
