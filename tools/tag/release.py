#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""tools/tag/release.py — 多仓 GitHub release 工具（v2）

设计原则
========

1. **每个仓的 release 只讲自己**。umbrella 的 release 才汇总全局兼容性矩阵；
   submodule 的 release 自包含（own info + commit + URL + 一句话「整体看 umbrella」）。
2. **不复制别人的代码 / zip 进自己的 release**。GitHub 自带的 source zip 已经是该仓自己的，
   就不再做手工 artifact 上传。
3. **annotated tag**：业界规范的发版做法，message 跟 tag 实际指向的 commit 一致。
4. **幂等**：tag 已存在 → upsert；release 已存在 → 默认 PATCH 更新（可关）。

CLI
===

A) 多仓 batch（标准用法）：

   python release.py --manifest examples/om-datacenter-v1.0.0.json

B) 干跑：

   python release.py --manifest examples/om-datacenter-v1.0.0.json --dry-run

C) 只重打 tag、不动 release：

   python release.py --manifest examples/om-datacenter-v1.0.0.json --tag-only

D) 只 PATCH release body、不动 tag：

   python release.py --manifest examples/om-datacenter-v1.0.0.json --body-only

E) 单仓发版（极简用法，不走 manifest）：

   python release.py \\
       --owner opensourceways --repo my-svc --branch main --tag v1.0.0 \\
       --title "v1.0.0" \\
       --body-file notes/body.md \\
       --tag-message-file notes/tag.txt

Manifest 结构
============

见 examples/om-datacenter-v1.0.0.json。最小骨架：

    {
      "tag": "v1.0.0",
      "date": "2026-05-15",
      "tagger": { "name": "...", "email": "..." },
      "umbrella": {
          "owner": "...", "name": "...", "branch": "main",
          "body_template_file": "umbrella-body.template.md",
          "tag_message_template_file": "umbrella-tag-message.txt",
          "title_template": "...",
          "context": {  ...任意 {placeholder} 渲染上下文... }
      },
      "submodules": [
        { "owner": "...", "name": "...", "branch": "...",
          "body_template_file": "submodule-body.template.md",
          "tag_message_template_file": "submodule-tag-message.txt",
          "title_template": "...",
          "context": { "capability": "...", "known_limits": "..." } }
      ]
    }

每个仓的 release body / tag message 用 Python str.format 渲染，可用占位符：
- {owner} / {repo} / {branch} / {tag} / {date}
- {sha} / {sha_short}（仓 HEAD 的真实 SHA）
- {umbrella_owner} / {umbrella_repo} / {umbrella_tag_url}
- {matrix}（仅 umbrella；自动渲染的兼容性矩阵 markdown）
- 以及 `context` 字段里的任意自定义键

Token
=====

按优先级：`--token` > `GITHUB_TOKEN` env > `GH_TOKEN` env > spec 仓 .git/config 嵌入 PAT。
PAT 需要 scope：`contents: write`（建 tag + release）；fine-grained PAT 加 `metadata: read`。
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

API = 'https://api.github.com'


# ──────────────────────────── helpers ────────────────────────────


def err(*args: Any) -> None:
    print(*args, file=sys.stderr)


def get_token(explicit: str | None) -> str:
    if explicit:
        return explicit
    for env in ('GITHUB_TOKEN', 'GH_TOKEN'):
        v = os.environ.get(env)
        if v:
            return v
    for p in (
        os.environ.get('SPEC_REPO_PATH'),
        r'C:\zhongjun\code\upstream\metrics\agent-development-all\agent-development-specification',
    ):
        if not p or not os.path.isdir(p):
            continue
        try:
            url = subprocess.check_output(
                ['git', '-C', p, 'config', 'remote.origin.url'],
                stderr=subprocess.DEVNULL, encoding='utf-8',
            ).strip()
            m = re.search(r'(ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+)', url)
            if m:
                return m.group(1)
        except subprocess.CalledProcessError:
            pass
    raise RuntimeError('no GitHub token; set GITHUB_TOKEN env or pass --token')


def _headers(token: str) -> dict[str, str]:
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json; charset=utf-8',
    }


def api(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, Any]:
    url = path if path.startswith('http') else f'{API}{path}'
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(token))
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def read_file(base_dir: str, path: str | None) -> str:
    if not path:
        return ''
    full = path if os.path.isabs(path) else os.path.join(base_dir, path)
    with open(full, encoding='utf-8') as f:
        return f.read()


def render(template: str, ctx: dict) -> str:
    if not template:
        return ''
    try:
        return template.format(**ctx)
    except KeyError as e:
        raise RuntimeError(f'template references undefined placeholder: {e}; ctx keys = {sorted(ctx.keys())}')


# ──────────────────────────── GitHub primitives ────────────────────────────


def branch_sha(owner: str, repo: str, branch: str, token: str) -> str:
    code, body = api('GET', f'/repos/{owner}/{repo}/branches/{branch}', token)
    if code != 200:
        raise RuntimeError(f'GET branch {owner}/{repo}#{branch} → {code}: {body}')
    return body['commit']['sha']


def existing_tag_target(owner: str, repo: str, tag: str, token: str) -> tuple[str | None, str | None]:
    """Return (target_commit_sha, ref_object_type) for an existing tag, or (None, None)."""
    code, body = api('GET', f'/repos/{owner}/{repo}/git/refs/tags/{tag}', token)
    if code == 404:
        return (None, None)
    if code != 200:
        raise RuntimeError(f'GET ref tags/{tag} → {code}: {body}')
    obj_type = body['object']['type']
    if obj_type == 'tag':
        c2, b2 = api('GET', f'/repos/{owner}/{repo}/git/tags/{body["object"]["sha"]}', token)
        if c2 != 200:
            raise RuntimeError(f'GET git/tags → {c2}: {b2}')
        return (b2['object']['sha'], 'tag')
    return (body['object']['sha'], 'commit')


def create_annotated_tag(owner: str, repo: str, *, tag: str, message: str,
                         target_sha: str, tagger_name: str, tagger_email: str,
                         token: str) -> str:
    """Create tag object and (re-)point refs/tags/<tag> at it. Returns tag-object SHA."""
    payload = {
        'tag': tag, 'message': message, 'object': target_sha, 'type': 'commit',
        'tagger': {
            'name': tagger_name, 'email': tagger_email,
            'date': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        },
    }
    code, body = api('POST', f'/repos/{owner}/{repo}/git/tags', token, payload)
    if code != 201:
        raise RuntimeError(f'POST git/tags → {code}: {body}')
    tag_obj_sha = body['sha']

    # upsert ref
    code, body = api('GET', f'/repos/{owner}/{repo}/git/refs/tags/{tag}', token)
    if code == 200:
        c, b = api('PATCH', f'/repos/{owner}/{repo}/git/refs/tags/{tag}', token,
                   {'sha': tag_obj_sha, 'force': True})
        if c != 200:
            raise RuntimeError(f'PATCH ref → {c}: {b}')
    elif code == 404:
        c, b = api('POST', f'/repos/{owner}/{repo}/git/refs', token,
                   {'ref': f'refs/tags/{tag}', 'sha': tag_obj_sha})
        if c != 201:
            raise RuntimeError(f'POST ref → {c}: {b}')
    else:
        raise RuntimeError(f'GET ref tags/{tag} → {code}: {body}')
    return tag_obj_sha


def existing_release(owner: str, repo: str, tag: str, token: str) -> dict | None:
    code, body = api('GET', f'/repos/{owner}/{repo}/releases/tags/{tag}', token)
    if code == 404:
        return None
    if code != 200:
        raise RuntimeError(f'GET release tag {tag} → {code}: {body}')
    return body


def upsert_release(owner: str, repo: str, *, tag: str, branch: str, title: str,
                   body: str, draft: bool, prerelease: bool, token: str) -> tuple[str, dict]:
    existing = existing_release(owner, repo, tag, token)
    if existing:
        code, resp = api('PATCH', f'/repos/{owner}/{repo}/releases/{existing["id"]}', token, {
            'tag_name': tag, 'target_commitish': branch,
            'name': title, 'body': body, 'draft': draft, 'prerelease': prerelease,
        })
        if code != 200:
            raise RuntimeError(f'PATCH release → {code}: {resp}')
        return ('updated', resp)
    code, resp = api('POST', f'/repos/{owner}/{repo}/releases', token, {
        'tag_name': tag, 'target_commitish': branch,
        'name': title, 'body': body, 'draft': draft, 'prerelease': prerelease,
        'generate_release_notes': False,
    })
    if code != 201:
        raise RuntimeError(f'POST release → {code}: {resp}')
    return ('created', resp)


# ──────────────────────────── domain model ────────────────────────────


@dataclasses.dataclass
class RepoSpec:
    owner: str
    name: str
    branch: str
    role: str  # 'umbrella' | 'submodule'
    body_template_file: str | None
    tag_message_template_file: str | None
    title_template: str
    context: dict  # custom render context (capability, known_limits, etc.)


@dataclasses.dataclass
class Plan:
    tag: str
    date: str
    tagger_name: str
    tagger_email: str
    draft: bool
    prerelease: bool
    repos: list[RepoSpec]  # umbrella first, then submodules


def parse_manifest(path: str) -> Plan:
    with open(path, encoding='utf-8') as f:
        m = json.load(f)

    repos: list[RepoSpec] = []

    if 'umbrella' in m:
        u = m['umbrella']
        repos.append(RepoSpec(
            owner=u['owner'], name=u['name'], branch=u.get('branch', 'main'),
            role='umbrella',
            body_template_file=u.get('body_template_file'),
            tag_message_template_file=u.get('tag_message_template_file'),
            title_template=u.get('title_template', '{tag}'),
            context=u.get('context', {}),
        ))
    for s in m.get('submodules', []) or []:
        repos.append(RepoSpec(
            owner=s['owner'], name=s['name'], branch=s.get('branch', 'main'),
            role='submodule',
            body_template_file=s.get('body_template_file'),
            tag_message_template_file=s.get('tag_message_template_file'),
            title_template=s.get('title_template', '{tag}'),
            context=s.get('context', {}),
        ))

    tagger = m.get('tagger', {})
    return Plan(
        tag=m['tag'],
        date=m.get('date', dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')),
        tagger_name=tagger.get('name', 'github-actions[bot]'),
        tagger_email=tagger.get('email', 'github-actions[bot]@users.noreply.github.com'),
        draft=bool(m.get('draft', False)),
        prerelease=bool(m.get('prerelease', False)),
        repos=repos,
    )


def build_compatibility_matrix(repos: list[RepoSpec], shas: dict[str, str]) -> str:
    """Markdown table covering all repos in the plan. umbrella row first."""
    rows = [
        '| 角色 | 仓库 | 分支 | 锁定 SHA |',
        '|---|---|---|---|',
    ]
    for r in repos:
        sha = shas[r.name][:10]
        rows.append(
            f'| {"🌐 umbrella" if r.role == "umbrella" else "📦 submodule"} '
            f'| [`{r.owner}/{r.name}`](https://github.com/{r.owner}/{r.name}/tree/{sha}) '
            f'| `{r.branch}` '
            f'| [`{sha}`](https://github.com/{r.owner}/{r.name}/commit/{sha}) |'
        )
    return '\n'.join(rows)


# ──────────────────────────── main flow ────────────────────────────


def process_plan(plan: Plan, *, base_dir: str, token: str,
                 tag_only: bool, body_only: bool, dry_run: bool,
                 use_tag_target: bool) -> list[dict]:
    """Execute the plan. If use_tag_target=True, use existing tag's target as SHA (not branch HEAD)."""
    # Resolve SHAs (per repo)
    shas: dict[str, str] = {}
    for r in plan.repos:
        if use_tag_target:
            sha, _ = existing_tag_target(r.owner, r.name, plan.tag, token)
            if sha is None:
                raise RuntimeError(f'{r.owner}/{r.name}: tag {plan.tag} not found; cannot use --use-tag-target')
        else:
            sha = branch_sha(r.owner, r.name, r.branch, token)
        shas[r.name] = sha
        print(f'  resolved {r.owner}/{r.name}@{r.branch} = {sha[:10]}')

    matrix_md = build_compatibility_matrix(plan.repos, shas)

    # Locate umbrella for back-link in submodule bodies
    umbrella = next((r for r in plan.repos if r.role == 'umbrella'), None)
    umbrella_ctx = {}
    if umbrella:
        umbrella_ctx = {
            'umbrella_owner': umbrella.owner,
            'umbrella_repo': umbrella.name,
            'umbrella_tag_url': f'https://github.com/{umbrella.owner}/{umbrella.name}/releases/tag/{plan.tag}',
            'umbrella_repo_url': f'https://github.com/{umbrella.owner}/{umbrella.name}',
        }

    results: list[dict] = []
    for r in plan.repos:
        sha = shas[r.name]
        ctx = {
            'owner': r.owner,
            'repo': r.name,
            'branch': r.branch,
            'tag': plan.tag,
            'date': plan.date,
            'sha': sha,
            'sha_short': sha[:10],
            'repo_url': f'https://github.com/{r.owner}/{r.name}',
            'commit_url': f'https://github.com/{r.owner}/{r.name}/commit/{sha}',
            'source_zip_url': f'https://github.com/{r.owner}/{r.name}/archive/refs/tags/{plan.tag}.zip',
            'source_tgz_url': f'https://github.com/{r.owner}/{r.name}/archive/refs/tags/{plan.tag}.tar.gz',
            'matrix': matrix_md if r.role == 'umbrella' else '',
            **umbrella_ctx,
            **r.context,
        }

        body_tmpl = read_file(base_dir, r.body_template_file)
        tag_tmpl = read_file(base_dir, r.tag_message_template_file) or body_tmpl

        body = render(body_tmpl, ctx) if body_tmpl else ''
        tag_msg = render(tag_tmpl, ctx) if tag_tmpl else body
        title = render(r.title_template, ctx)

        result: dict[str, Any] = {
            'repo': f'{r.owner}/{r.name}', 'role': r.role,
            'sha': sha, 'actions': [],
        }

        # 1. tag
        if not body_only:
            if dry_run:
                result['actions'].append(f'would create annotated tag {plan.tag} → {sha[:10]}')
            else:
                tag_obj_sha = create_annotated_tag(
                    r.owner, r.name,
                    tag=plan.tag, message=tag_msg, target_sha=sha,
                    tagger_name=plan.tagger_name, tagger_email=plan.tagger_email,
                    token=token,
                )
                result['actions'].append(f'annotated tag → {tag_obj_sha[:10]} (points-at commit {sha[:10]})')

        # 2. release
        if not tag_only:
            if dry_run:
                result['actions'].append('would upsert release')
            else:
                action, rel = upsert_release(
                    r.owner, r.name,
                    tag=plan.tag, branch=r.branch, title=title, body=body,
                    draft=plan.draft, prerelease=plan.prerelease, token=token,
                )
                result['actions'].append(f'release {action} → {rel["html_url"]}')
                result['release_url'] = rel['html_url']

        results.append(result)
    return results


# ──────────────────────────── CLI ────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--manifest', help='JSON manifest path.')
    # single-repo mode (no manifest)
    p.add_argument('--owner')
    p.add_argument('--repo')
    p.add_argument('--branch', default='main')
    p.add_argument('--tag')
    p.add_argument('--title')
    p.add_argument('--body-file')
    p.add_argument('--tag-message-file')
    p.add_argument('--tagger-name', default='github-actions[bot]')
    p.add_argument('--tagger-email', default='github-actions[bot]@users.noreply.github.com')
    p.add_argument('--draft', action='store_true')
    p.add_argument('--prerelease', action='store_true')
    # modes
    p.add_argument('--tag-only',  action='store_true', help='Only (re-)create tag, no release.')
    p.add_argument('--body-only', action='store_true', help='Only upsert release body, no tag.')
    p.add_argument('--use-tag-target', action='store_true',
                   help='Use existing tag\'s target commit instead of branch HEAD (for re-rendering historical releases).')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--token')
    return p


def main(argv: list[str]) -> int:
    # Windows + Python 3.14 default stdout = cp1252; force utf-8 so 中文 / emoji 不炸
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
    args = build_parser().parse_args(argv)
    if args.tag_only and args.body_only:
        err('ERR --tag-only and --body-only are mutually exclusive')
        return 2
    token = get_token(args.token)

    if args.manifest:
        plan = parse_manifest(args.manifest)
        base = os.path.dirname(os.path.abspath(args.manifest))
    else:
        if not (args.owner and args.repo and args.tag):
            err('ERR single-repo mode needs --owner --repo --tag (or use --manifest)')
            return 2
        base = '.'
        # body-file / tag-message-file are paths; pass through directly to context
        plan = Plan(
            tag=args.tag,
            date=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d'),
            tagger_name=args.tagger_name, tagger_email=args.tagger_email,
            draft=args.draft, prerelease=args.prerelease,
            repos=[RepoSpec(
                owner=args.owner, name=args.repo, branch=args.branch,
                role='submodule',  # treat as standalone
                body_template_file=args.body_file,
                tag_message_template_file=args.tag_message_file or args.body_file,
                title_template=args.title or args.tag,
                context={},
            )],
        )

    results = process_plan(
        plan, base_dir=base, token=token,
        tag_only=args.tag_only, body_only=args.body_only, dry_run=args.dry_run,
        use_tag_target=args.use_tag_target,
    )

    print('\n==== summary ====')
    for r in results:
        url = r.get('release_url', '')
        print(f'  [{r["role"]:9}] {r["repo"]:38} sha={r["sha"][:10]}  {url}')
        for a in r['actions']:
            print(f'    · {a}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
