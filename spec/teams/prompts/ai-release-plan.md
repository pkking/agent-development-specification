根据版本发布 Issue 和仓库 Tag 差异，自动编写变更计划说明书。

## 输入参数
- $ARGUMENTS: release-mgmt Issue + 仓库@Tag 对（空格分隔）
  - 格式：`release-mgmt#N repo1@tag1 [repo2@tag2...]`
  - 示例：`release-mgmt#5 infra-community@v1.2.0 robot-gitee-openeuler-ci@v0.8.0`
  - **release-mgmt#N**：版本发布 Issue 编号（用于归档和关联）
  - **repo@tag**：仓库名@base tag，自动比较该仓库主干分支（或用户指定的 release 分支）与 base tag 的差异，提取关联 Issue

## 核心理念
> 变更计划基于（仓库 + base tag）差异自动发现关联 Issue 和 PR：
> - 输入 release-mgmt Issue 编号 + 一组仓库@tag 对
> - 自动 diff 各仓库主干分支（main/master）或用户指定的 release 分支与 base tag，提取差异中关联的 Issue
> - 基于发现的 Issue 和 PR 编写统一的变更计划说明书
> - 变更计划必须关联所有业务 PR（backlog 仓以外），建立完整追溯链
> - 归档统一到 release-mgmt 仓
> - 每次实践产生复利：完成后沉淀经验到 context/experience/

## 参考规范
- 变更计划模板：`templates/Release/#1 xx Change Plan Specification.md`
- 编写经验：`context/experience/变更计划编写经验.md`
- 设计和开发规范：`context/team/` 目录

## 执行步骤

### 第一步：解析输入并获取差异 Issue

**解析输入参数**：
1. 提取 `release-mgmt#N` → 版本发布 Issue 编号
2. 提取所有 `repo@tag` 对 → 仓库名和 base tag 列表

**获取 release-mgmt Issue 信息**：
1. 使用 `gh api repos/opensourceways/release-mgmt/issues/{issueNumber}` 获取 Issue 信息
2. 解析版本名称、发布描述

**自动发现各仓库差异关联的 Issue**：

对每个 `repo@tag` 对：
1. **确定比较分支**：默认为 main/master；如用户指定了 release 分支（如 `releaseXX`），使用该分支
2. **获取 tag 到分支的 commit 差异**：
   ```bash
   gh api repos/opensourceways/{repo}/compare/{tag}...{branch} --jq '.commits[].commit.message'
   ```
3. **从 commit message 中提取关联 Issue**：
   - 匹配模式：`#N`、`fixes #N`、`closes #N`、`resolve #N`、`{owner}/{repo}#N`、Issue URL
   - 去重并记录每个 Issue 的来源仓库
4. **获取差异中的 PR**：
   ```bash
   gh api repos/opensourceways/{repo}/compare/{tag}...{branch} --jq '.commits[].commit.message' | grep -oP '#\d+'
   ```
   或通过 PR merge commit 识别：
   ```bash
   gh api "repos/opensourceways/{repo}/pulls?state=closed&base={branch}&sort=updated&direction=desc" --jq '[.[] | select(.merged_at != null)]'
   ```
5. **补充：通过 GitHub Search 查找关联 PR**：
   ```bash
   gh api "search/issues?q=repo:opensourceways/{repo}+is:pr+is:merged+linked:issue" --jq '.items[] | {number, title, html_url}'
   ```

**汇总发现的 Issue 和 PR**：

| 仓库 | Issue | 标题 | 关联 PR | 来源（commit/PR） |
|------|-------|------|--------|-----------------|

**检查外部平台 Issue**：扫描 Issue body 和 commit message 中的外部平台链接（gitcode.com、gitee.com 等）；如用户在会话中提供了额外的外部平台 Issue 链接，一并记录。

### 第二步：收集各关联 Issue 的详细信息

对每个发现的关联 Issue：
1. 使用 `gh api repos/{owner}/{repo}/issues/{number}` 获取 Issue 详情（标题、标签、状态）
2. **识别 Issue 来源平台**：
   - GitHub Issue：使用 `gh api repos/{owner}/{repo}/issues/{number}/timeline` 或搜索关联 PR
   - GitCode Issue：Issue body 中如包含 GitCode 链接（`gitcode.com`），使用 GitCode API 获取关联 PR（见「第三方平台 PR 获取」）
   - 其他平台：根据 Issue body 中的链接特征识别，使用对应 API
3. 收集每个 Issue 关联的业务 PR 链接（backlog 仓以外的 PR）
4. **获取每个业务 PR 的代码变更内容**（见「第二步附2：获取 PR 代码变更」）
5. **读取 Issue 生命周期文档**（见「第二步附1：读取生命周期文档」）
6. 汇总信息：

| 仓库 | Issue | 标题 | 变更类型 | 关联 PR | 状态 |
|------|-------|------|---------|--------|------|

#### 第二步附1：读取生命周期文档

对每个 backlog 仓的关联 Issue，读取其 `issue_docs/{issueId}/` 目录下的生命周期文档：

1. **需求分析**：`Requirement Analysis/#XX Requirement Analysis Specification.md`
   - 提取：功能范围、影响面、依赖关系
2. **架构设计**：`Architecture Desgin/#XX Architecture Design Specification.md`
   - 提取：技术方案、部署架构、服务间调用关系、配置项
3. **测试策略**：`Test/#XX Test Strategy.md`
   - 提取：测试范围、验证方法、关键验证点
4. **测试报告**：`Test/#XX Test Report.md`
   - 提取：测试结果、已验证场景、遗留风险

> **用途**：这些文档为后续编写「详细执行步骤」「生产环境验证」「回滚方案」提供依据。
> - 架构设计中的部署架构 → 指导执行步骤和发布顺序
> - 架构设计中的配置项 → 指导变更内容和回滚范围
> - 测试策略/报告中的验证方法 → 直接复用为生产验证方案
> - 需求分析中的影响面 → 指导回滚判断标准

> **注意**：文档不一定齐全，按实际存在的文档读取即可。非 backlog 仓的 Issue（如 jenkins-log-scanner#15）通常无本地文档，跳过。

#### 第二步附2：获取 PR 代码变更

对每个关联的业务 PR，获取代码变更详情：

1. **GitHub PR**：`gh api repos/{owner}/{repo}/pulls/{number}/files --jq '.[] | {filename, status, additions, deletions}'`
2. **GitCode PR**：`curl -H "Authorization: token {token}" "https://api.gitcode.com/api/v5/repos/{owner}/{repo}/pulls/{number}/files"`
3. 对核心代码仓（非部署脚本仓）的 PR，进一步获取 patch 内容以理解具体变更逻辑
4. 汇总变更内容，用于：
   - 编写「变更内容」章节：列出新增/修改/删除的文件及说明
   - 细化「详细执行步骤」：基于实际代码变更编写具体操作
   - 完善「生产环境验证」：基于实际变更点设计验证项
   - 完善「回滚方案」：基于实际变更范围确定回滚策略

> **部署脚本仓**（helm-charts、infra-community 等）：仅获取文件列表作为参考（如提取 namespace、镜像版本、资源配置等），不需要深入分析代码逻辑。

### 第三步：分析变更等级
根据所有关联变更综合判定版本级变更等级：

1. 逐项评估每个 Issue 的单项等级：
   - **L1**：涉及数据库 Schema、全局配置中心、网络拓扑
   - **L2**：微服务配置变更、非核心插件发布、新服务上线
   - **L3**：代码清理、Bug 修复、不影响逻辑的配置微调

2. 综合判定版本级等级：
   - 取所有单项等级的最高值
   - 如存在跨服务联动（多个仓库同时变更），等级可能需要上调

### 第四步：确定发布顺序
1. 分析各仓库间的依赖关系（基础配置 → 核心服务 → 依赖服务）
2. 生成发布顺序

### 第五步：编写变更计划说明书

**如果变更计划文件已存在**：执行「PR 描述刷新」（见第五步附），而非从头编写。

**创建目录**：`issue_docs/{issueId}/Release/`（本仓库根目录下）

**文件命名**：`#{issueId} {变更名称} Change Plan Specification.md`

基于模板 `templates/Release/#1 xx Change Plan Specification.md` 填写：

#### 1. 变更概览
- **需求或版本发布Task链接**：版本发布 Issue 链接
- **变更内容概要**：一句话概括本次变更的核心内容（做什么、涉及哪些仓库、部署到哪里）
- **关联测试报告链接**：如有（如不涉及可不填）
- **开发责任人**：各 Issue 的 assignee（仅填 ID，模板中 `_githubid & gitcodeid_` 为格式提示，不要复制到实际文档）
- **变更责任人**：版本发布负责人
- **变更时间**：计划发布时间（优先从 Issue 描述或里程碑提取，无则默认为文档编写日期 + 3 天，并提示用户确认）
- **变更等级**：综合判定结果（在对应等级前打勾 `[X]`）
- **关联Issue汇总**：表格列出所有发现的关联 Issue（列名：仓库、IssueUrl、标题、变更类型、关联业务 PR、PR 状态、Issue 状态）
- **关联业务 PR**：汇总所有关联的业务 PR（backlog 仓以外），格式 `org/repo#PRNumber`

#### 变更详细内容
基于 PR 代码变更，按仓库汇总本次版本发布的实际变更内容：

| 仓库 | PR | 变更文件 | 变更说明 |
|------|-----|---------|---------|
| {repo1} | #{PRNumber} | 新增/修改/删除的关键文件 | 变更的功能说明 |
| ... | ... | ... | ... |

> **编写依据**：第二步附2 获取的 PR 代码变更内容。
> **核心代码仓**：详细列出新增/修改/删除的文件及功能说明。
> **部署脚本仓**：仅列出关键配置（namespace、镜像版本、资源配置等）。

#### 2. 详细执行步骤
基于 PR 代码变更和生命周期文档（架构设计中的部署架构、配置项等），按发布顺序，为每个仓库编写原子化执行步骤：

| 步骤 | 操作类型 | 操作内容描述 | 预期结果 | 执行人 |
|------|---------|------------|---------|--------|
| 1 | 发布 {repo1} | 触发 {repo1} 发布流水线，选本分支 xxx | 流水线执行成功，生产部署完成 | @xxx |
| 2 | 验证 {repo1} | 检查 {repo1} 服务健康状态 | 服务正常运行 | @xxx |
| 3 | 发布 {repo2} | 触发 {repo2} 发布流水线 | 流水线执行成功 | @xxx |
| ... | ... | ... | ... | ... |

#### 3. 生产环境验证
基于 PR 代码变更和生命周期文档（测试策略中的验证方法、测试报告中的验证场景），编写具体验证方案：
- 各服务独立验证（健康检查、日志确认）
- 跨服务端到端验证（如有依赖关系）
- 具体验证命令/接口/日志关键词
- 复用测试报告中已验证的场景和方法

#### 4. 回滚方案
基于 PR 代码变更和生命周期文档（架构设计中的部署架构和配置项、需求分析中的影响面），编写回滚方案：
- 回滚触发条件
- 按发布顺序的逆序编写回滚步骤
- 明确是全量回退还是部分回退的判断标准

#### 第五步附：PR 描述刷新（每次执行必做）

无论变更计划是新建还是已存在，都必须执行以下刷新操作：

1. **获取每个关联 PR 的最新状态**：
   - GitHub PR：`gh api repos/{owner}/{repo}/pulls/{number} --jq '{number, title, state, merged, html_url}'`
   - GitCode PR：`curl -H "Authorization: token {token}" "https://api.gitcode.com/api/v5/repos/{owner}/{repo}/pulls/{number}"`
2. **更新变更计划中的 PR 信息**：
   - 关联 Issue 汇总表：更新 PR 状态列（已合入 / open / closed）
   - 执行步骤表：更新状态列（已完成 / 待验证 / 待开发）
   - 关联业务 PR 列表：同步 PR 标题和状态
3. **更新 release-mgmt Issue body**：
   - 刷新「发布进度」跟踪表中的 PR 状态
   - 如果有新增的 PR（新开发完成的功能），追加到列表中
   - 「任务描述」中的关联 Issue 使用完整 URL 链接（含外部平台 Issue）

> **刷新原则**：PR 标题、合入状态以实时 API 查询结果为准，不依赖缓存或上次记录。

### 第六步：创建 Release Tag 计划
在变更计划末尾追加版本号和 Tag 规划：

```markdown
## 5. 版本号与 Release Tag

| 仓库 | 版本号 | Tag 创建时机 |
|------|--------|------------|
| {repo1} | v{x.y.z} | 生产部署验证通过后 |
| {repo2} | v{x.y.z} | 生产部署验证通过后 |
```

### 第七步：更新 Issue 描述

使用 `gh api` 更新 release-mgmt Issue body，补充：
- 变更等级
- 发布顺序
- 变更计划文档链接
- 自动发现的关联 Issue 列表

**Issue 描述中的关联 Issue 必须使用完整链接**：
- GitHub Issue：`https://github.com/{owner}/{repo}/issues/{number}`（GitHub 页面可自动渲染）
- 外部平台 Issue（GitCode、Gitee 等）：GitHub 无法自动关联，必须显式写出完整 URL 并标注平台名
  - 示例：`[gitcode#123](https://gitcode.com/org/repo/issues/123) (GitCode)`
- 外部平台 Issue 链接来源：
  1. commit message 或 PR body 中可能包含外部平台链接
  2. 用户在会话中主动提供（如 `关联的 GitCode issue: https://gitcode.com/...`）
  3. 如果无法自动获取，向用户询问是否有关联的外部平台 Issue

**Issue body 格式规范**：
```markdown
### 任务描述

{版本发布描述}，包含以下需求：
- [{owner}/{repo}#{number}: {标题}]({完整URL})
- [{外部平台标识}#{number}: {标题}]({完整URL}) (GitCode)

### 比较基准
| 仓库 | Base Tag | 比较分支 |
|------|----------|---------|
| {repo1} | {tag1} | main |
| {repo2} | {tag2} | main |

### 变更等级
...
### 发布顺序
...
### 变更计划
...
### 发布进度
| 关联 PR | 仓库 | 标题 | 状态 |
...
```

### 第八步：经验沉淀【必选步骤，不可跳过】

1. **回顾本次编写过程**，提炼经验：
   - 跨仓库依赖分析是否有遗漏？
   - 等级判定是否有争议点？
   - 发布顺序是否有特殊考量？
   - Tag 差异发现 Issue 的准确性如何？是否有遗漏？

2. **更新 `context/experience/变更计划编写经验.md`**

3. **Skill 改进检测【必须执行】**：如发现改进点，主动询问用户是否更新 skill。

### 第九步：提交 PR

将本次变更的文件提交并创建 PR。

1. **确认分支**：检查当前分支是否为个人分支（如 `zkh`、`{username}` 等）
   - 如果在 `main` 或公共分支上：基于当前分支创建个人分支 `git checkout -b {username}/{short-description-in-kebab-case}`
   - 如果已在个人分支上：直接使用当前分支
2. **暂存变更文件**：`git add` 本次新建或修改的文件（变更计划、经验文档等）
3. **提交 commit**：
   ```bash
   git commit -m "docs: {简短描述，如 add #1 change plan specification}"
   ```
4. **推送并创建 PR**：
   ```bash
   git push -u origin {branch}
   gh pr create --title "{PR 标题}" --body "$(cat <<'EOF'
   ## 描述
   {本次变更描述，如：编写/刷新 #{issueId} 版本发布变更计划说明书}

   ## 相关 Issue
   resolve #{issueId}

   ## 变更类型
   - [ ] Bug 修复
   - [ ] 新功能
   - [ ] 代码重构
   - [X] 文档更新
   - [ ] 样式改进
   - [ ] 性能优化
   - [ ] 测试相关
   - [ ] 其他
   EOF
   )"
   ```

> **PR 模板**：遵循组织 PR 模板（描述、相关 Issue、变更类型三段式），变更类型默认勾选「文档更新」。
> **PR 标题**：`docs: #{issueId} {变更名称} change plan`，保持简短。

### 第十步：输出总结
1. 创建/更新的文件清单
2. 版本变更等级及判定理由
3. 发布顺序及依赖关系
4. 关联的所有业务 PR 列表
5. 各仓库 Tag 差异发现的 Issue 汇总
6. 本次沉淀的经验要点
7. **PR 链接**

## 关键规范
- **发布模式**：统一为一种模式——基于 release-mgmt Issue + 仓库@tag 对，自动 diff 发现关联 Issue
- **输入格式**：`release-mgmt#N repo1@tag1 [repo2@tag2...]`
- **比较分支**：默认为各仓库的 main/master 分支；用户可指定 release 分支（如 `releaseXX`）
- **Issue 发现**：从 tag 到分支的 commit 差异中自动提取关联 Issue（通过 commit message、PR 关联等）
- **文件命名**：`#{issueId}` 开头，issueId 为 release-mgmt Issue 的编号
- **关联业务 PR**：必须列出 backlog 仓以外的所有业务 PR，格式 `org/repo#PRNumber`
- **部署脚本仓库**：helm-charts、infra-community 等仓库为部署脚本仓，仅供参考（如获取部署配置、环境变量等），不作为核心服务仓库对待
- **发布顺序**：基础设施/配置先行，核心服务次之，依赖服务最后
- **回滚顺序**：与发布顺序相反
- **保留模板结构**：所有 `>` 引导提示和勾选项列表必须保留
- **版本号**：所有参与仓库使用统一版本号，格式 `v{major}.{minor}.{patch}`
- **Release Tag**：各仓库在生产部署验证通过后各自创建 GitHub Release Tag
- **归档位置**：统一归档到本仓库 `issue_docs/{issueId}/Release/`
- **生命周期文档**：编写变更计划前必须读取对应 Issue 的需求分析、架构设计、测试策略/报告文档，作为执行步骤、验证方案和回滚方案的依据
- **平台标注**：如非 GitHub，在 PR 链接后标注平台名，如 `(GitCode)`

## 第三方平台 PR 获取

### 平台识别

关联 Issue 可能涉及第三方平台的仓库和 PR。通过以下方式识别：
- Issue body 或 commit message 中包含 `gitcode.com` 链接 → GitCode 平台
- Issue body 或 commit message 中包含 `gitee.com` 链接 → Gitee 平台
- Issue 标签或标题中标注了平台信息

### GitCode API

GitCode 使用 Gitea API v5，认证通过 HTTP Header 传递（避免 Token 出现在 URL 参数中）。

**获取仓库 PR 列表**：
```bash
curl -H "Authorization: token {token}" "https://api.gitcode.com/api/v5/repos/{owner}/{repo}/pulls?state=all"
```

**获取单个 PR 详情**：
```bash
curl -H "Authorization: token {token}" "https://api.gitcode.com/api/v5/repos/{owner}/{repo}/pulls/{number}"
```

**搜索关联 PR**（通过 Issue 编号）：
- 在 PR 列表中按标题或 body 搜索 Issue 编号
- 或通过 Issue 的 timeline/events API 查找引用

**Token 配置**：环境变量 `GITCODE_TOKEN`。

### Gitee API（预留）

如未来涉及 Gitee 平台仓库，使用 Gitee API v5：
```bash
curl -H "Authorization: token {token}" "https://gitee.com/api/v5/repos/{owner}/{repo}/pulls?state=all"
```

### PR 信息格式统一

不论来源平台，变更计划中 PR 信息统一记录以下字段：
- **PR 链接**：完整 URL
- **PR 标题**：从 API 实时获取
- **PR 状态**：open / merged / closed
- **平台标注**：如非 GitHub，在 PR 链接后标注平台名，如 `(GitCode)`
