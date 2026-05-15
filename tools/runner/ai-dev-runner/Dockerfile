# ai-dev-runner — 跑流程 1 / 2 / 3 主体的 self-hosted runner
# 镜像构建：./build-and-push.sh
FROM ubuntu:24.04

ARG GH_RUNNER_VERSION=2.317.0
ARG TARGETARCH=amd64

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl wget git jq unzip xz-utils gnupg lsb-release \
      build-essential python3 python3-pip python3-venv \
      nodejs npm \
      openjdk-17-jre-headless maven \
      sudo iproute2 \
    && rm -rf /var/lib/apt/lists/*

# kubectl + helm
RUN curl -fsSL -o /usr/local/bin/kubectl \
      "https://dl.k8s.io/release/$(curl -fsSL https://dl.k8s.io/release/stable.txt)/bin/linux/${TARGETARCH}/kubectl" \
    && chmod +x /usr/local/bin/kubectl

RUN curl -fsSL https://baltocdn.com/helm/signing.asc | gpg --dearmor -o /usr/share/keyrings/helm.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" \
       > /etc/apt/sources.list.d/helm-stable-debian.list \
    && apt-get update && apt-get install -y --no-install-recommends helm \
    && rm -rf /var/lib/apt/lists/*

# gh CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=${TARGETARCH} signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Claude CLI (Anthropic)
RUN npm install -g @anthropic-ai/claude-code

# Non-root runner user
RUN useradd -m -s /bin/bash runner && echo "runner ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/runner

USER runner
WORKDIR /home/runner

# Install GitHub Actions runner
RUN mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner \
    && curl -fsSL -o runner.tar.gz \
       "https://github.com/actions/runner/releases/download/v${GH_RUNNER_VERSION}/actions-runner-linux-${TARGETARCH}-${GH_RUNNER_VERSION}.tar.gz" \
    && tar xzf runner.tar.gz && rm runner.tar.gz

COPY --chown=runner:runner --chmod=755 entrypoint.sh start-runner.sh /home/runner/

ENTRYPOINT ["/home/runner/entrypoint.sh"]
