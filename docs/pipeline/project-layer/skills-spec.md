# 项目层 skills 规范

> 项目仓 `skills/` 目录可放项目专属 skill，作为团队 prompt 之外的额外能力。

## 1. 何时需要 skill

- 项目专属的频繁操作（如「给 om-datacenter 新增一个社区」「给 X 服务接 OAuth」）
- 操作步骤超过 3 步、且会被反复触发
- 仅团队 prompt + 项目 CLAUDE.md 不足以覆盖

## 2. 文件结构

每个 skill 一个独立目录：

```
projects/<project>/skills/
├─ <skill-name>/
│  ├─ SKILL.md      ← skill 描述 + 触发关键词 + 步骤
│  └─ <补充文件>     ← 可选
```

## 3. SKILL.md 必含段

| 段 | 内容 |
|---|---|
| 名称 | 与目录同名 |
| 触发词 | AI 何时该用本 skill |
| 步骤 | 编号步骤，每步可执行 |
| 输入 | 必备入参 |
| 输出 | 期望产出 |
| 关联 | 团队规范 / 项目文档 / 其他 skill |

## 4. 模板

- 模板：[`../../projects/template/skills/skill-name.md.tmpl`](../../projects/template/skills/)
- 实例参考：[`../../projects/om-datacenter/skills/`](../../projects/om-datacenter/skills/)

## 5. 不允许

- 在 SKILL.md 里写真实凭据
- 抄团队规范全文（应链接到 `teams/standards/...`）
