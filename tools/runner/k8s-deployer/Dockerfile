# k8s-deployer — 把构建产物部署到 K8s 的 self-hosted runner
FROM ubuntu:24.04

ARG GH_RUNNER_VERSION=2.317.0
ARG TARGETARCH=amd64

ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl wget git jq unzip gnupg lsb-release \
      python3 python3-pip sudo \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /usr/local/bin/kubectl \
      "https://dl.k8s.io/release/$(curl -fsSL https://dl.k8s.io/release/stable.txt)/bin/linux/${TARGETARCH}/kubectl" \
    && chmod +x /usr/local/bin/kubectl

RUN curl -fsSL https://baltocdn.com/helm/signing.asc | gpg --dearmor -o /usr/share/keyrings/helm.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" \
       > /etc/apt/sources.list.d/helm-stable-debian.list \
    && apt-get update && apt-get install -y --no-install-recommends helm \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash deployer && echo "deployer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/deployer

USER deployer
WORKDIR /home/deployer

RUN mkdir -p /home/deployer/actions-runner && cd /home/deployer/actions-runner \
    && curl -fsSL -o runner.tar.gz \
       "https://github.com/actions/runner/releases/download/v${GH_RUNNER_VERSION}/actions-runner-linux-${TARGETARCH}-${GH_RUNNER_VERSION}.tar.gz" \
    && tar xzf runner.tar.gz && rm runner.tar.gz

COPY --chown=deployer:deployer --chmod=755 entrypoint.sh start-runner.sh /home/deployer/

ENTRYPOINT ["/home/deployer/entrypoint.sh"]
