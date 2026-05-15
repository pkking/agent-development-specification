#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""tools/tag/release.py — 给一个或多个 GitHub 仓打 annotated tag + 发布 release。

按业界规范（SemVer + annotated tag + 结构化 release notes）的「one-shot 基线发布」工具。
适合 umbrella + 多 submodule 项目（如 om-datacenter）同时发版的场景，也适合单仓发版。

用法
====

A) 单仓：

  python release.py \\
      --owner opensourceways \\
      --repo  om-datacenter \\
      --branch main \\
      --tag   v1.0.0 \\
      --title "v1.0.0 — 数据中台基线版本" \\
      --body-file notes/om-datacenter-v1.0.0.md \\
      --tag-message-file notes/baseline-tag-message.txt

B) 多仓（manifest 模式）：

  python release.py --manifest examples/om-datacenter-v1.0.0.json

  manifest 文件结构见 examples/om-datacenter-v1.0.0.json。

C) 升级既有 lightweight tag 为 annotated（不动 release 内容）：

  python release.py --owner opensourceways --repo om-datacenter --tag v1.0.0 \\
      --tag-message-file notes/baseline-tag-message.txt --upgrade-annotated-only

Token
=====

PAT 来源（按优先级）：
  1. --token <pat>
  2. env GITHUB_TOKEN
  3. env GH_TOKEN
  4. spec 仓 .git/config remote origin url 里嵌的 PAT（开发机本地约定）

PAT 需要 scope：
  - 仓 `contents: write`（建 tag + release）
  - org-level 用 fine-grained PAT 时同时勾 `metadata: read`
"""
from __future__ import annotations

import argparse
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


def stderr(*args: Any) -> None:
    print(*args, file=sys.stderr)


def get_token(explicit: str | None) -> str:
    if explicit:
        return explicit
    for env in ('GITHUB_TOKEN', 'GH_TOKEN'):
        v = os.environ.get(env)
        if v:
            return v
    # fallback: spec repo's .git/config remote URL
    candidates = [
        os.environ.get('SPEC_REPO_PATH'),
        r'C:\zhongjun\code\upstream\metrics\agent-development-all\agent-development-specification',
    ]
    for p in candidates:
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


def headers(token: str) -> dict[str, str]:
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json; charset=utf-8',
    }


def api_request(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, Any]:
    url = path if path.startswith('http') else f'{API}{path}'
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers(token))
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


def read_file(path: str | None) -> str | None:
    if not path:
        return None
    with open(path, encoding='utf-8') as f:
        return f.read()


# ──────────────────────────── core operations ────────────────────────────


def get_branch_sha(owner: str, repo: str, branch: str, token: str) -> str:
    code, body = api_request('GET', f'/repos/{owner}/{repo}/branches/{branch}', token)
    if code != 200:
        raise RuntimeError(f'GET branch {owner}/{repo}#{branch} → HTTP {code}: {body}')
    return body['commit']['sha']


def tag_ref_exists(owner: str, repo: str, tag: str, token: str) -> tuple[bool, str | None, str | None]:
    """Return (exists, ref_sha, ref_obj_type)."""
    code, body = api_request('GET', f'/repos/{owner}/{repo}/git/refs/tags/{tag}', token)
    if code == 404:
        return (False, None, None)
    if code != 200:
        raise RuntimeError(f'GET ref tags/{tag} → HTTP {code}: {body}')
    return (True, body['object']['sha'], body['object']['type'])


def release_exists(owner: str, repo: str, tag: str, token: str) -> dict | None:
    code, body = api_request('GET', f'/repos/{owner}/{repo}/releases/tags/{tag}', token)
    if code == 404:
        return None
    if code != 200:
        raise RuntimeError(f'GET release tag {tag} → HTTP {code}: {body}')
    return body


def create_tag_object(owner: str, repo: str, *, tag: str, message: str,
                      target_sha: str, tagger_name: str, tagger_email: str,
                      token: str) -> str:
    """Create annotated tag object. Returns the tag object SHA (not the commit SHA)."""
    payload = {
        'tag': tag,
        'message': message,
        'object': target_sha,
        'type': 'commit',
        'tagger': {
            'name': tagger_name,
            'email': tagger_email,
            'date': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        },
    }
    code, body = api_request('POST', f'/repos/{owner}/{repo}/git/tags', token, payload)
    if code != 201:
        raise RuntimeError(f'POST git/tags → HTTP {code}: {body}')
    return body['sha']


def upsert_tag_ref(owner: str, repo: str, *, tag: str, target_sha: str, token: str) -> None:
    """Create or force-update the refs/tags/<tag> ref to point at target_sha."""
    exists, _, _ = tag_ref_exists(owner, repo, tag, token)
    if exists:
        code, body = api_request(
            'PATCH', f'/repos/{owner}/{repo}/git/refs/tags/{tag}', token,
            {'sha': target_sha, 'force': True},
        )
        if code != 200:
            raise RuntimeError(f'PATCH ref tags/{tag} → HTTP {code}: {body}')
    else:
        code, body = api_request(
            'POST', f'/repos/{owner}/{repo}/git/refs', token,
            {'ref': f'refs/tags/{tag}', 'sha': target_sha},
        )
        if code != 201:
            raise RuntimeError(f'POST git/refs (new tag) → HTTP {code}: {body}')


def create_release(owner: str, repo: str, *, tag: str, branch: str, title: str,
                   body: str, draft: bool, prerelease: bool, token: str) -> dict:
    payload = {
        'tag_name': tag,
        'target_commitish': branch,
        'name': title,
        'body': body,
        'draft': draft,
        'prerelease': prerelease,
        'generate_release_notes': False,
    }
    code, resp = api_request('POST', f'/repos/{owner}/{repo}/releases', token, payload)
    if code != 201:
        raise RuntimeError(f'POST releases → HTTP {code}: {resp}')
    return resp


# ──────────────────────────── high-level flow ────────────────────────────


def process_one_repo(*, owner: str, repo: str, branch: str, tag: str,
                     tag_message: str, title: str | None, body: str | None,
                     tagger_name: str, tagger_email: str,
                     skip_release: bool, draft: bool, prerelease: bool,
                     upgrade_annotated_only: bool,
                     dry_run: bool, token: str) -> dict:
    """Do tag + release on one repo. Idempotent: re-running upgrades lightweight→annotated."""
    summary: dict[str, Any] = {'repo': f'{owner}/{repo}', 'actions': []}

    # 1. resolve target SHA
    if upgrade_annotated_only:
        exists, ref_sha, obj_type = tag_ref_exists(owner, repo, tag, token)
        if not exists:
            raise RuntimeError(f'{owner}/{repo}: tag {tag} does not exist; cannot upgrade')
        # Lightweight: object.type == "commit", points directly at commit
        # Annotated:   object.type == "tag",    points at a tag object
        target_sha = ref_sha
        if obj_type == 'tag':
            # already annotated; resolve the tag object's commit
            code, body_obj = api_request('GET', f'/repos/{owner}/{repo}/git/tags/{ref_sha}', token)
            if code != 200:
                raise RuntimeError(f'GET git/tags/{ref_sha} → HTTP {code}: {body_obj}')
            target_sha = body_obj['object']['sha']
            summary['note'] = 'tag was already annotated; refreshed message anyway'
    else:
        target_sha = get_branch_sha(owner, repo, branch, token)
    summary['target_sha'] = target_sha

    # 2. create annotated tag object
    if dry_run:
        summary['actions'].append('would create annotated tag object')
        summary['actions'].append(f'would upsert refs/tags/{tag} → tag object')
    else:
        tag_obj_sha = create_tag_object(
            owner, repo,
            tag=tag, message=tag_message, target_sha=target_sha,
            tagger_name=tagger_name, tagger_email=tagger_email, token=token,
        )
        summary['tag_object_sha'] = tag_obj_sha
        summary['actions'].append('created annotated tag object')

        # 3. upsert ref
        upsert_tag_ref(owner, repo, tag=tag, target_sha=tag_obj_sha, token=token)
        summary['actions'].append(f'pointed refs/tags/{tag} at tag object')

    # 4. release (skip if upgrade-only or skip_release)
    if upgrade_annotated_only or skip_release:
        summary['release'] = 'skipped'
        return summary

    existing = release_exists(owner, repo, tag, token)
    if existing:
        summary['release'] = 'exists'
        summary['release_url'] = existing['html_url']
    elif dry_run:
        summary['actions'].append('would create release')
        summary['release'] = 'dry-run'
    else:
        if not title:
            title = tag
        if body is None:
            body = tag_message  # fallback
        rel = create_release(
            owner, repo, tag=tag, branch=branch, title=title, body=body,
            draft=draft, prerelease=prerelease, token=token,
        )
        summary['release'] = 'created'
        summary['release_url'] = rel['html_url']

    return summary


def load_manifest(path: str) -> dict:
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def render(template: str, ctx: dict) -> str:
    """Plain str.format style template (no jinja dep). Use {name} placeholders."""
    if not template:
        return ''
    return template.format(**ctx)


# ──────────────────────────── CLI ────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Tag + release tool for GitHub repos (annotated tags by default).')
    p.add_argument('--manifest', help='JSON manifest for multi-repo batch (see examples/).')
    p.add_argument('--owner', help='GitHub owner (single-repo mode).')
    p.add_argument('--repo', help='Repo name (single-repo mode).')
    p.add_argument('--branch', help='Source branch for tag target (default: main).')
    p.add_argument('--tag', help='Tag name, e.g. v1.0.0.')
    p.add_argument('--title', help='Release title.')
    p.add_argument('--body-file', help='Release body markdown file.')
    p.add_argument('--tag-message-file', help='Annotated tag message file (defaults to body-file).')
    p.add_argument('--tagger-name', default='opensourceways-bot')
    p.add_argument('--tagger-email', default='noreply@opensourceways.org')
    p.add_argument('--draft', action='store_true')
    p.add_argument('--prerelease', action='store_true')
    p.add_argument('--skip-release', action='store_true', help='Only create/upgrade tag, no release.')
    p.add_argument('--upgrade-annotated-only', action='store_true',
                   help='Convert existing lightweight tag to annotated without touching release.')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--token', help='GitHub PAT; otherwise env GITHUB_TOKEN/GH_TOKEN or spec repo PAT.')
    return p


def cmd_single(args: argparse.Namespace, token: str) -> int:
    required = ['owner', 'repo', 'tag']
    missing = [n for n in required if not getattr(args, n)]
    if missing:
        stderr(f'ERR single-repo mode missing: {missing}')
        return 2

    body = read_file(args.body_file) or ''
    tag_msg = read_file(args.tag_message_file) or body
    if not tag_msg:
        stderr('ERR need --tag-message-file (or --body-file).')
        return 2

    branch = args.branch or 'main'
    title = args.title or args.tag

    summary = process_one_repo(
        owner=args.owner, repo=args.repo, branch=branch, tag=args.tag,
        tag_message=tag_msg, title=title, body=body,
        tagger_name=args.tagger_name, tagger_email=args.tagger_email,
        skip_release=args.skip_release, draft=args.draft, prerelease=args.prerelease,
        upgrade_annotated_only=args.upgrade_annotated_only,
        dry_run=args.dry_run, token=token,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_batch(args: argparse.Namespace, token: str) -> int:
    m = load_manifest(args.manifest)
    base_dir = os.path.dirname(os.path.abspath(args.manifest))

    tag = m['tag']
    date = m.get('date', dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d'))
    tagger_name = m.get('tagger', {}).get('name', args.tagger_name)
    tagger_email = m.get('tagger', {}).get('email', args.tagger_email)
    draft = m.get('draft', args.draft)
    prerelease = m.get('prerelease', args.prerelease)

    def load_rel(rel_path: str) -> str:
        return read_file(os.path.join(base_dir, rel_path)) or ''

    tag_msg_tmpl = (m.get('tag_message') or
                    load_rel(m['tag_message_file']) if m.get('tag_message_file') else '')
    body_tmpl = (m.get('body_template') or
                 load_rel(m['body_template_file']) if m.get('body_template_file') else '')
    title_tmpl = m.get('release_title_template', tag)

    # Phase 1: resolve every repo's "anchor" SHA for the matrix + render context.
    # Normal mode: branch HEAD at run time.
    # Upgrade-annotated-only: the actual commit the existing tag points at (so the
    # tag message stays consistent with where the tag is anchored).
    pre: list[dict] = []
    for r in m['repos']:
        if args.upgrade_annotated_only:
            exists, ref_sha, obj_type = tag_ref_exists(r['owner'], r['name'], tag, token)
            if not exists:
                raise RuntimeError(f'{r["owner"]}/{r["name"]}: tag {tag} not found; cannot upgrade')
            if obj_type == 'tag':
                code, tag_obj = api_request('GET', f'/repos/{r["owner"]}/{r["name"]}/git/tags/{ref_sha}', token)
                sha = tag_obj['object']['sha']
            else:
                sha = ref_sha
        else:
            sha = get_branch_sha(r['owner'], r['name'], r.get('branch', 'main'), token)
        pre.append({**r, 'sha': sha})
        print(f"  resolved {r['owner']}/{r['name']}@{r.get('branch','main')} = {sha[:10]}")

    matrix_rows = '\n'.join(
        f"| `{p['name']}` | [`{p['owner']}/{p['name']}`](https://github.com/{p['owner']}/{p['name']}/tree/{p['sha'][:10]}) | `{p.get('branch','main')}` | `{p['sha'][:10]}` | {p.get('role','—')} |"
        for p in pre
    )
    matrix = (
        '| 组件 | 仓库 | 分支 | 锁定 SHA | 角色 |\n'
        '|---|---|---|---|---|\n'
        + matrix_rows
    )

    # Phase 2: process each repo
    summaries = []
    for p in pre:
        ctx = {
            'tag': tag,
            'date': date,
            'owner': p['owner'],
            'repo': p['name'],
            'branch': p.get('branch', 'main'),
            'sha': p['sha'],
            'sha_short': p['sha'][:10],
            'role': p.get('role', ''),
            'role_label': p.get('role_label', p.get('role', '')),
            'capability': p.get('capability', ''),
            'matrix': matrix if p.get('include_matrix') else '',
            'extra': p.get('body_extra', ''),
        }
        title = render(title_tmpl, ctx)
        body = render(body_tmpl, ctx)
        tag_msg = render(tag_msg_tmpl, ctx) if tag_msg_tmpl else body

        s = process_one_repo(
            owner=p['owner'], repo=p['name'], branch=p.get('branch', 'main'),
            tag=tag, tag_message=tag_msg, title=title, body=body,
            tagger_name=tagger_name, tagger_email=tagger_email,
            skip_release=args.skip_release, draft=draft, prerelease=prerelease,
            upgrade_annotated_only=args.upgrade_annotated_only,
            dry_run=args.dry_run, token=token,
        )
        summaries.append(s)
        print(f"\n==== {s['repo']} ====")
        print(json.dumps(s, ensure_ascii=False, indent=2))

    print('\n==== summary ====')
    for s in summaries:
        rel = s.get('release_url') or s.get('release', '')
        print(f"  {s['repo']:34} {' '.join(s['actions']):60} release={rel}")
    return 0


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    token = get_token(args.token)
    if args.manifest:
        return cmd_batch(args, token)
    return cmd_single(args, token)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
