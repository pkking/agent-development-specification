# 流水线治理：现状盘点 + 决策待拍板

> 目的：流水线/文档散落在 6+ 仓、职责重叠、触发词混乱，本文把现状摊开，
> 列出**必须由你拍板的争议点**（每条给推荐 + 备选 + 优缺点），拍完按结论收敛。
> 这是「决策记录」性质文档，不替代 [`architecture.md`](architecture.md)（那是收敛后的目标态）。

## 1. 现状全景（谁在哪、干啥）

```
阶段          实现位置（仓 / workflow）                                          重叠?
────────────────────────────────────────────────────────────────────────────────
Issue 提交     backlog 仓 Issue 模板                                              —
响应&菜单      backlog/services-menu.yml（forward + 贴菜单 + dispatch 外仓）       —
需求分析       om-datacenter/issue-1  ≈  backlog/analyze-requirement   ★双实现
开发+预览      om-datacenter/issue-2  ≈  backlog/implement              ★双实现
               （二者都调同一个 om-datacenter/src/orchestrate.sh 四 agent 对抗）
测试           orchestrate.sh 内 tester + backlog/test-python.yml                 —
合入+上 beta   om-datacenter/issue-3（merge PR → deployer promote beta）          —
发布上线       release-mgmt/release.yml（通用配置驱动）                  ★三实现
               om-datacenter/release-datastat-manage-website.yml（datastat 专用）
               om-datacenter/issue-3 里的 deployer promote（也能上线）
变更计划       release-mgmt/workflow_change.yml（AI 生成变更计划 PR）             —
旁支-PR预览    om-datacenter/pr-deploy-preview.yml（k8s-deployer）                —
旁支-门禁      APIMagic/datastat/om-dataarts 各 5 个（gate/label/branch/scan）  ★三仓复制
旁支-同步      om-datacenter/apimagic-make|reload|sync-* + sync-pg（手工孤岛）    —
旁支-通用bot   om-datacenter/opencode.yml（/oc，独立体系）                        —
```

runner 标签现有 7 种：`ai-dev-runner` / `ai-design-runner` / `ai-develop-runner` /
`k8s-deployer` / `dataarts-local` / 裸 `self-hosted` / `ubuntu-latest`。

## 2. 核心问题（盘点出的，归并为 6 类）

| #   | 问题                                                                                                                                                                                                          | 影响                                        |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| P1  | **需求分析/开发 在 om-datacenter 与 backlog 各实现一遍**（issue-1≈analyze-requirement, issue-2≈implement），核心逻辑近似复制，仅 backlog 多一层 services.yaml 精筛                                            | 改一处忘另一处 → 行为漂移；新人不知该看哪套 |
| P2  | **发布上线 3 条路径**：release-mgmt 通用 / datastat 专用 / issue-3 deployer promote，目标重叠（datastat 至少 3 条都能上线）；release.yml 注释自承"由 datastat 迁移并通用化"=未清理残留                        | 上线入口不唯一，责任不清                    |
| P3  | **触发词体系无规范**：上线就有 `[小数需求上线]`/`[小数合入上线]`/`[数据中台合入上线]` 3 别名；分析/实现各有 `[小数*]`/`[数据中台*]`/`[机器人*]`；release-mgmt 又另起 `同意发布`                               | 用户记不住、文档对不上、易触发错流程        |
| P4  | **dev 子仓 5-workflow 复制粘贴**（APIMagic/datastat/om-dataarts 各一份 gate/label/branch/scan），且 datastat 已私自漂移（gate-check 多加 feature/staging 分支；label-check.yml 内容错放成 branch-check 逻辑） | N 份拷贝改不动；已出 bug                    |
| P5  | **runner label 7 种散落**，注释里带"绕配额"临时说明，无统一拓扑文档                                                                                                                                           | 不知道哪个 job 该跑哪、扩容/迁移无依据      |
| P6  | **手工孤岛 & 坏件**：apimagic-make/reload/sync-\* 纯手动与主线无衔接、sync-pg 写死内网 IP/pod 名；om-deployment/yaml-validation.yml 内联 Python 缩进 bug 必报错；opencode.yml 用独立 secret 体系平行存在      | 名存实亡的门禁、隐性故障、凭据体系割裂      |

## 3. 三套治理方案（优缺点对比）

### 方案 A：单 Hub 收敛（backlog 为唯一编排入口）

所有 issue/分析/实现/合入触发都进 backlog，om-datacenter 退化为「被编排的工具+dev 仓集合」，发布统一走 release-mgmt。

- ✅ 入口唯一，触发词只在 backlog 维护一套；新增服务只改 backlog/services/\*.yaml
- ✅ 与"backlog 已是多服务接入口"的现状一致，改动方向顺势
- ❌ 要废弃 om-datacenter 的 issue-1/2/3（迁移成本、历史 dispatch 链路要清）
- ❌ backlog 仓变重，权限/审计集中

### 方案 B：分层收敛（编排留 om-datacenter，backlog 只做 forward）

om-datacenter 保留 issue-1/2/3 为唯一编排实现；backlog 只保留 services-menu 的「贴菜单+forward dispatch」，删掉 backlog 自跑的 analyze/implement。发布统一 release-mgmt。

- ✅ 改动最小（删 backlog 的重复实现即可，编排大脑 orchestrate.sh 不动）
- ✅ 职责清晰：backlog=入口路由，om-datacenter=编排执行，release-mgmt=发布
- ❌ 仍是跨仓 dispatch 链路（forward → dispatch → umbrella），调试链长
- ❌ backlog 与 om-datacenter 仍耦合（forward 要知道 umbrella 的触发词）

### 方案 C：维持现状 + 只修 bug + 加规范文档

不动架构，只修 P4/P6 的坏件、补触发词规范文档和 runner 拓扑文档、删 release-datastat 残留。

- ✅ 零迁移风险，最快止血
- ❌ P1/P2/P3 结构性重复没解决，半年后继续烂
- ❌ 文档与实现"两套并存"的根因还在

> 倾向：**方案 B**（性价比最高，删重复即可，不重写编排大脑）；P4 无论选哪个方案都要做（抽 reusable workflow）。

## 4. 待你拍板的争议点（逐条给推荐）

| 编号 | 争议点                | 推荐                                                                                                                                                | 备选                                     | 取舍                                                              |
| ---- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------- | -------------------- | -------------------- |
| D1   | 编排入口收敛到哪？    | **方案 B**：om-datacenter 唯一编排，backlog 只 forward                                                                                              | 方案 A（backlog 单 Hub）/ 方案 C（维持） | B 改动最小且职责清；A 更彻底但迁移贵                              |
| D2   | 发布上线唯一入口？    | **release-mgmt/release.yml 为唯一生产发布**；issue-3 只到 beta；**废弃 release-datastat-manage-website.yml**                                        | 保留 datastat 专用作过渡                 | 三合一消除 P2，datastat 用 release-config 接入即可                |
| D3   | 触发词规范            | \*\*统一 `[<服务名>需求分析                                                                                                                         | 实现                                     | 上线]`+ 发布侧`同意发布`\*\*，旧别名标 deprecated 保留 1 季度兼容 | 立即删旧别名（硬切） | 渐进不破坏存量 issue |
| D4   | dev 子仓 5-workflow   | **抽成 org 级 reusable workflow**（`opensourceways/.github` 或 spec 仓模板），各仓只留 1 个 caller                                                  | 脚手架定期同步拷贝                       | reusable 根治漂移；脚手架仍会漂                                   |
| D5   | runner 拓扑           | **合并 ai-design/ai-develop → ai-dev-runner 一种**（按 label 区分无必要），出一份 [`generic-layer/runners.md`](generic-layer/runners.md) 唯一拓扑表 | 维持多 label                             | 少一种 label 少一份维护；除非有硬隔离需求                         |
| D6   | 手工同步类 workflow   | **显式归类「运维手动工具」**单独目录/文档，不混进主线；修 sync-pg 硬编码                                                                            | 纳入自动主线                             | 它们本就是 break-glass，强行自动化风险大                          |
| D7   | opencode.yml 通用 bot | **保留为 break-glass 应急通道**，文档标注与主线体系独立、用独立 secret                                                                              | 废弃                                     | 应急通道有价值，但要写清边界                                      |
| D8   | 坏件修复优先级        | **P0 立即修**：datastat label-check.yml 错放、om-deployment yaml-validation 缩进 bug                                                                | 排期                                     | 名存实亡的门禁=安全隐患，优先                                     |

## 4.5 凭据 / 镜像 / 环境隔离 决策项（D9–D17，**新增，与 D1–D8 平行待拍板**）

> 背景：变更发布已真实跑通（演练态）。要上正式必须先定清「秘钥放哪、怎么变、镜像放哪、
> test/beta/prod 怎么隔离、beta 改完怎么保证 prod 升级不出事」。下列每条给推荐+备选+取舍，
> 末尾「D17」是**我替你补的、你没列但必须一起定**的点。

| 编号    | 决策点                                                              | 推荐                                                                                                                                                                                                                | 备选                                                                                    | 取舍 / 风险                                                                                                                                  |
| ------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **D9**  | **秘钥存哪**                                                        | **分层**：CI 触发类（RELEASE_MGMT_TOKEN/OPENCODE_API_KEY/SOURCE_REPO_TOKEN）→ GitHub repo Secret；运行时业务凭据（DB/Redis/第三方）→ 每环境独立 **External-Secrets Operator(ESO) + 后端 KMS/Vault** 注入 K8s Secret | 全 Vault sidecar / 全 K8s Secret 手工 / 全 GitHub Secret                                | 现状是 GitHub+K8s+少量 Vault 三处混存（om-datacenter 历史）→ 散乱。统一 ESO 一处真相、自动轮换；迁移有成本                                   |
| **D10** | **秘钥跨环境一致还是不一致**                                        | **同名异值**：secret 的 **KEY/名一致**（manifest、workflow、配置可跨环境移植），**VALUE 每环境独立**（test/beta/prod 各自 DB/API 凭据物理隔离，互不可达）                                                           | 完全同值（省事但 prod 凭据等于裸奔）/ 完全独立命名（配置无法移植，每环境改 manifest）   | 这是关键原则：**名一致保证"测过的配置=上线的配置"，值隔离保证爆炸半径**。不一致命名会让发布流水线没法通用                                    |
| **D11** | **beta 改完怎么保证 prod 自动升级不出事**（你的核心担忧）           | promote 前加 **「秘钥形态对账门禁」**：比对 beta 与 prod 的 secret **KEY 集合 + 配置项 schema 是否齐**（**只比键/形态，绝不比值**），prod 缺键即 **fail-fast 拦停** 并提示「先在 prod 配齐 X 再 promote」           | 人工 checklist / 不校验（出事再说）                                                     | 根因：beta 新增了一个 secret/配置项、prod 没有 → prod 滚动升级即 CrashLoop。形态对账把"漏配"在发布前挡住；值不一致是设计预期（见 D10）不报错 |
| **D12** | **秘钥变更 / 轮换流程**                                             | prod secret 变更：**双人审批 + 审计留痕 + 先在 beta 验证同形态变更 + ESO 自动 rollout + 旧值保留回滚窗口**；定期轮换；泄露应急 SOP（rotate → 按 D10 只影响该环境）                                                  | 谁有权谁改（无门禁）/ 永不轮换                                                          | 不定轮换 SOP，泄露时不知道波及哪些环境；prod 直改无双人=高危单点                                                                             |
| **D13** | **镜像仓库放哪 + 隔离**                                             | **test=集群内 registry**（image.mode=local，免云凭据，现状）；**beta/prod=华为云 SWR 但强隔离**：prod **独立账号/独立 project/独立拉取凭据**，beta 独立 project（与 test/prod 都不共享）                            | beta 复用 test 集群内 registry（持久性差）/ test、beta、prod 同一 SWR project（不隔离） | prod 与 test 共 registry = test 侧失陷可投毒 prod 镜像。账号级隔离最稳，project 级最低要求                                                   |
| **D14** | **镜像晋级方式**                                                    | **构建一次、按 digest 不可变晋级** test→beta→prod（retag/复制 manifest，不各环境重 build）                                                                                                                          | 每环境各自重新 build                                                                    | 重 build 会导致"beta 测的二进制 ≠ prod 上线的二进制"，扫描/测试白做。不可变晋级=可追溯、可签名                                               |
| **D15** | **test/beta/prod 隔离档位**（你问的"prod/beta 要隔离吧"——对，必须） | **prod = 独立集群 + 独立云账号 + 独立 registry + 独立 secret store**（最高隔离）；**beta = 至少独立 namespace + 独立 secret store，理想独立集群**；test = 现 ai-test 集群                                           | 三环境同集群不同 ns（最弱）/ test+beta 同集群、prod 独立（折中）                        | prod 同集群=一次配置错/越权即全毁。**注意现状风险**：test 集群与 ai-dev-runner 同集群，runner 持集群凭据，是横向移动面（见 D17）             |
| **D16** | **GitOps 部署仓与 secret 边界**                                     | **infra-common 只放 image tag + 非敏感配置，绝不放任何 secret 值**；secret 由每环境 ESO/SealedSecret 独立管，部署仓只引用 secret **名**                                                                             | 部署仓放加密 secret（SealedSecret 入仓）/ 明文（绝不）                                  | 部署仓是多人可读的 GitOps 真相源，放值=泄露面最大。引用名+环境侧注入是业界标准                                                               |

### D17 — 我替你补的、你没列但必须一起定的点

1. **回滚与 secret/schema 漂移**：镜像能回滚，但若期间 DB schema / secret 形态已变，回滚镜像会跑不起来。变更计划的「回滚方案」必须含 **secret/schema 维度的回滚兼容性判断**（是否可纯镜像回滚 / 需连带回滚配置）。
2. **runner 横向移动风险**：当前 `ai-dev-runner` 与 test 集群同处、持集群凭据。**正式发布的 runner 必须独立、最小权限、不与 dev/test runner 混**，否则 dev 侧失陷可触达发布链路与 test secret。
3. **配置/秘钥漂移检测**：定期 diff `beta vs prod` 的 secret KEY 集合与配置项并告警，防"beta 加了 prod 没加"静默积累（这是 D11 的常态化版本）。
4. **镜像来源证明**：prod 镜像应 **cosign 签名 + SBOM**，配合 image-vuln-scan，确保上线的镜像可追溯、未被篡改。
5. **长期 admin PAT 风险**：现 `SOURCE_REPO_TOKEN` 用的是某人 admin PAT clone 私有源码仓——**应换成 fine-grained 只读 / deploy key / 短时 token**，避免长期高权限凭据进 CI。
6. **审计**：所有 prod secret 读写 + 发布触发（谁、何时、改了什么）必须可审计留痕。
7. **多区域/容灾**（若 prod 跨区）：secret 与 registry 的跨区复制一致性策略。

> 这些都未拍板。建议与 D1–D8 一起过；D9–D16 是上正式的**前置硬约束**（不定清不能上 prod），
> D17 各条按风险排期。本节不改 D1–D8 / §5 / §6。

## 4.6 已落地（真实验证，供决策参考）

> 通用机制层面已实现并真跑验证的几项（robot 服务专属细节不在此处，见
> [robot 示例](../specification-example/project/robot/README.md)）：

- **AI-native 模板 + accepted 自动起分析**（通用）：组织通用 issue 模板仓追加带「目标服务」
  下拉的模板（**不覆盖**业务仓既有模板），配通用 `auto-analyze-on-accept` workflow ——
  打 `accepted` 后自动进流程 1，**减少 D3 提到的人工触发词依赖**（D3 仍待拍板，这是其
  渐进落地的一部分，非替代决策）。
- **多服务接入已验证 2 个**：datacenter（umbrella 多仓）+ robot（单仓），证明通用层
  「加一个 `services/<id>.yaml` + 一个 tools_repo」即可接新服务，workflow/脚本零改 ——
  与 D1（编排入口收敛）方向一致。
- **归档/不可达 dev 仓护栏生效**：dev agent 对归档仓正确判 `mode=none` 拒绝伪造（呼应
  D17「回滚/不可达」类风险与既有 hard-gate 教训）。

> 本节为进展记录，不改任何 D 决策项，不替代拍板。

## 5. 拍板后落地顺序（建议）

1. D8 坏件（P0，1 天）→ 2. D2 发布三合一（删 datastat 专用，datastat 走 release-config）→
2. D1/B 删 backlog 重复实现 → 4. D3 触发词规范文档 + deprecated 标注 →
3. D4 reusable workflow 抽取 → 6. D5 runner 拓扑文档 → 7. D6/D7 归类与边界文档。

每项落地后回写 [`architecture.md`](architecture.md) 对应段，保持「文档=收敛后目标态」单一真相。

## 6. 关联

- 目标态全景：[`architecture.md`](architecture.md)
- 变更发布治理：[`change-release-process.md`](change-release-process.md)
- 发布过程：[`release-process.md`](release-process.md)
- Runner（待补唯一拓扑）：[`generic-layer/runners.md`](generic-layer/runners.md)
