# 项目层 CLAUDE.md 规范

> 项目仓根目录的 `CLAUDE.md` 是 AI agent 进入项目时的第一份必读文件。

## 1. 必含段

| 段           | 内容                                                                                         |
| ------------ | -------------------------------------------------------------------------------------------- |
| 项目档位     | A 档 / B 档（声明本项目接入到哪档）                                                          |
| 触发词       | 列全部 `[<服务名>需求]` / `[<服务名>需求分析]` / `[<服务名>需求实现]` / `[<服务名>需求上线]` |
| 项目铁规     | 必须 / 禁止做的项目专属事项（覆盖团队规范）                                                  |
| 子仓清单     | 如果是 umbrella 项目（如 om-datacenter），列子仓                                             |
| 部署模式     | dev-pod / data-pod / shared / none                                                           |
| 白名单       | maintainer 名单（用于流程 3 白名单校验）                                                     |
| 凭据清单链接 | 指向项目 `docs/credentials-inventory.md`                                                     |
| 关联         | 通用流水线 / 团队规范 / 项目模板                                                             |

## 2. 占位符

- `<<PROJECT_NAME>>`
- `<<PROJECT_DISPLAY_NAME>>`
- `<<TRIGGER_PREFIX>>`（可多个，逗号分隔）
- `<<DEV_REPOS>>`
- `<<DEPLOY_MODE>>`
- `<<BASE_DOMAIN>>`
- `<<NAMESPACE>>`
- `<<MAINTAINER_WHITELIST>>`

接入时逐项替换。

## 3. 与三层规范关系

```
个人层 ~/.claude/CLAUDE.md  > 项目层 CLAUDE.md（本文档） > 团队层 teams/CLAUDE.md
```

## 4. 模板

- 模板：[`../../projects/template/CLAUDE.md.tmpl`](../../projects/template/CLAUDE.md.tmpl)
- 实例：[`../../projects/om-datacenter/CLAUDE.md`](../../projects/om-datacenter/CLAUDE.md)

## 5. 不允许

- 直接抄团队 CLAUDE.md 内容（直接 link 即可）
- 写入真实凭据 / 内网域名 / 完整 IP
- 引用外部 GitHub / GitCode URL，应链接到本仓相对路径
