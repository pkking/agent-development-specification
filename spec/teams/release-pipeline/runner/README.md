# release-mgmt self-hosted runner 部署

> 让 `workflow_change.yml` / `release.yml`（`runs-on: [self-hosted, ai-dev-runner]`）
> 在 release-mgmt 真正跑起来。需要**集群 kubeconfig**（AI 侧无此凭据，必须运维执行）。

## 为什么需要这一步

GitHub 仓库级 self-hosted runner 只服务单仓。已有的 `ai-dev-runner` 注册在
`opensourceways/om-datacenter`，**不会**接 release-mgmt 的 job。所以 release-mgmt
要么单独起一个 runner（本目录方案，推荐），要么把 ai-dev-runner 升级为组织级。

## 一次性部署（运维，需 ai-test 集群 kubeconfig）

```bash
# 1. 取 release-mgmt 的 runner 注册 token（admin PAT；token ~1h 过期，现取现用）
REG_TOKEN=$(curl -sS -X POST \
  -H "Authorization: token <ADMIN_PAT>" \
  https://api.github.com/repos/opensourceways/release-mgmt/actions/runners/registration-token \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')

# 2. 建/更新 k8s Secret（注意：REG_TOKEN 是敏感值，勿写进任何文件/提交）
kubectl -n ai-test create secret generic release-mgmt-runner-secrets \
  --from-literal=GITHUB_URL=https://github.com/opensourceways/release-mgmt \
  --from-literal=RUNNER_TOKEN="$REG_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. 部署 runner
kubectl apply -f release-mgmt-runner.yaml

# 4. 确认已注册
kubectl -n ai-test rollout status deploy/release-mgmt-runner
gh api repos/opensourceways/release-mgmt/actions/runners --jq '.runners[].name'
```

## 本地镜像构建（image.mode=local）额外前置

`release.yml` 正式发布走 containerd 构建。runner 默认镜像**不含**构建链，需运维：

1. 在 runner 镜像加 `nerdctl`（推荐）或 `buildah`+`ctr`
2. 解开 `release-mgmt-runner.yaml` 里 `containerd-sock` 的注释（挂 `/run/containerd/containerd.sock`）
3. 节点 containerd 的 k8s.io namespace 可被 runner 访问

未配齐时 `scripts/build_image.py` 会**明确报错并打印该补什么**，不会静默假成功。
演练态（评论 `同意发布`，不带「正式」）不触发真实构建，无需上述前置。

## 仓库 Secret / Variable（运维在 GitHub Settings 配，AI 不代填真值）

见 [`../../AGENTS.md`](../../AGENTS.md) §运行前置：

- 必需：`RELEASE_APPROVERS`(Variable，真实审批人 GitHub 登录名)、
  `RELEASE_MGMT_TOKEN`(Secret，repo+workflow scope PAT)、`OPENCODE_API_KEY`(Secret)
- 条件：`SWR_*`(仅 image.mode=swr)、`INFRA_COMMON_REPO_TOKEN`(仅 deploy.mode≠none)

> AI 无法代为部署：本地无集群 kubeconfig；且不臆造任何密钥值/审批人名单。
> 以上步骤齐全后，在 release-mgmt 提变更 Issue 即可端到端真实跑。
