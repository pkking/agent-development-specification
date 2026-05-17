"""检查阶段单项执行（真实，无 dry 跳过）。用法：python run_check.py <check>

check ∈ secret-scan | change-plan-integrity | sast | vuln-scan | license-compliance | ut-coverage

- secret-scan / change-plan-integrity：对 release-mgmt 的 issue_docs/<N>/Release（硬门禁）
- sast / vuln-scan / license-compliance / ut-coverage：clone 被发布服务源码仓**真扫**
  · 演练/正式都真跑（扫描只读，安全）；不再因 dry 跳过
  · runner 缺扫描工具时**运行时自动安装**（semgrep 用 pip、trivy 下静态二进制）；
    实在装不上才 SKIP（只读检查不挡发布，与服务侧 CI 互补）
  · 工具命中严重问题 → exit 1（fail-fast 停整条）

环境变量：ISSUE_NUMBER, CONFIG_JSON；SOURCE_REPO_TOKEN 优先（能 clone 私有源码仓）回退 GH_TOKEN
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys

from release_lib import scan_sensitive

check = sys.argv[1] if len(sys.argv) > 1 else ""
ISSUE = os.environ["ISSUE_NUMBER"]
cfg = json.loads(os.environ.get("CONFIG_JSON", "{}"))
SRC = "_src_check"
BIN = os.path.abspath(".rmbin")  # 运行时安装的工具放这，加进 PATH


def which(*n):
    for x in n:
        p = shutil.which(x)
        if p:
            return p
    return None


def ok(msg):
    print(f"✓ {check}: {msg}")
    sys.exit(0)


def fail(msg):
    print(f"::error::{check}: {msg}")
    sys.exit(1)


def skip(msg):
    print(f"::notice::{check} SKIP: {msg}（只读检查，不挡发布，与服务侧 CI 互补）")
    sys.exit(0)


def clone_src():
    if os.path.isdir(SRC):
        shutil.rmtree(SRC, ignore_errors=True)
    tok = os.environ.get("SOURCE_REPO_TOKEN") or os.environ.get("GH_TOKEN", "")
    repo = cfg["source_repo"]
    br = cfg.get("default_branch", "main")
    url = f"https://x-access-token:{tok}@github.com/{repo}.git" if tok else f"https://github.com/{repo}.git"
    r = subprocess.run(["git", "clone", "--depth", "1", "--branch", br, url, SRC],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        err = (r.stderr or "")
        if tok:
            err = err.replace(tok, "***")
        fail(f"clone 源码仓 {repo}@{br} 失败（exit {r.returncode}）。"
             f"需 SOURCE_REPO_TOKEN 能 clone 该私有仓。详情：{err.strip()[:200]}")


def ensure_semgrep():
    p = which("semgrep")
    if p:
        return p
    # 运行时装：pip 用户级
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                    "--disable-pip-version-check", "--user", "semgrep"],
                   check=False)
    return which("semgrep") or shutil.which(
        "semgrep", path=os.path.join(os.path.expanduser("~"), ".local", "bin"))


def ensure_trivy():
    p = which("trivy")
    if p:
        return p
    os.makedirs(BIN, exist_ok=True)
    inst = subprocess.run(
        "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh "
        f"| sh -s -- -b {BIN} >/dev/null 2>&1", shell=True)
    cand = os.path.join(BIN, "trivy")
    return cand if (inst.returncode == 0 and os.path.exists(cand)) else None


if check == "secret-scan":
    hits = scan_sensitive(f"issue_docs/{ISSUE}")
    if hits:
        for h in hits[:20]:
            print("  " + h)
        fail("变更计划命中敏感信息")
    ok("无敏感信息")

elif check == "change-plan-integrity":
    mds = glob.glob(f"issue_docs/{ISSUE}/Release/*.md")
    if not mds:
        fail("变更计划不存在")
    txt = open(mds[0], encoding="utf-8", errors="ignore").read()
    miss = [n for n in ("详细执行步骤", "回滚方案") if n not in txt]
    if miss:
        fail(f"变更计划缺章节：{miss}")
    ok(f"完整：{os.path.basename(mds[0])}")

elif check == "sast":
    clone_src()
    sg = ensure_semgrep()
    if not sg:
        skip("semgrep 运行时安装失败")
    # 团队门禁政策（对齐 om-datacenter codearts-gates）：仅 ERROR 级阻断发布，
    # WARNING/INFO 不挡（p/security-audit 在大仓 warning 噪声极多，全卡不合理）。
    # --severity ERROR 只评估 ERROR 规则；--error 仅当存在 ERROR findings 时非 0。
    r = subprocess.run([sg, "--config", "p/security-audit", "--severity", "ERROR",
                        "--error", "--quiet", "--no-git-ignore", SRC])
    if r.returncode != 0:
        fail("semgrep 发现 ERROR 级安全问题（p/security-audit）——需修复源码后重发")
    ok("semgrep 真扫通过（无 ERROR 级；WARNING/INFO 不阻断，与团队门禁政策一致）")

elif check == "vuln-scan":
    # vuln_block：默认 True（发现 CRITICAL/HIGH 即阻断）；服务在变更计划书面记录
    # 风险接受后可在 release-config 设 checks.vuln_block=false → 仅告警不阻断。
    block = cfg.get("checks", {}).get("vuln_block", True)
    clone_src()
    if os.path.exists(os.path.join(SRC, "package.json")) and which("npm"):
        r = subprocess.run(["npm", "audit", "--audit-level=high"], cwd=SRC)
        if r.returncode != 0:
            if block:
                fail("npm audit 报 high+ 漏洞")
            print("::warning::npm audit 报 high+ 漏洞——vuln_block=false，仅告警不阻断（风险已在变更计划记录）")
            ok("npm audit 真扫完成（告警模式）")
        ok("npm audit 真扫通过")
    tv = ensure_trivy()
    if not tv:
        skip("trivy 运行时安装失败且非 npm 项目")
    r = subprocess.run([tv, "fs", "--severity", "CRITICAL,HIGH", "--exit-code", "1",
                        "--ignore-unfixed", "--quiet", "--no-progress", SRC])
    if r.returncode != 0:
        if block:
            fail("trivy fs 发现 CRITICAL/HIGH 漏洞——需升级依赖后重发（如需带漏洞发布，"
                 "在变更计划书面记录风险接受并将 release-config 的 checks.vuln_block 设 false）")
        print("::warning::trivy fs 发现 CRITICAL/HIGH 漏洞——vuln_block=false，仅告警不阻断"
              "（风险已在变更计划书面记录接受）")
        ok("trivy fs 真扫完成（告警模式，未阻断）")
    ok("trivy fs 真扫通过")

elif check == "license-compliance":
    clone_src()
    if not os.path.exists(os.path.join(SRC, "package.json")):
        skip("非 node 项目（license-checker 仅覆盖 npm 依赖；Java/Python 由服务侧 CI 保证）")
    npx = which("npx")
    if not npx:
        skip("runner 无 npx")
    r = subprocess.run([npx, "--yes", "license-checker-rseidelsohn",
                        "--production", "--failOn", "GPL;AGPL;LGPL",
                        "--excludePrivatePackages"], cwd=SRC)
    if r.returncode != 0:
        fail("依赖含 GPL/AGPL/LGPL 强传染协议")
    ok("license 真扫合规")

elif check == "ut-coverage":
    clone_src()
    pj = os.path.join(SRC, "package.json")
    if os.path.exists(pj):
        sc = (json.load(open(pj, encoding="utf-8")) or {}).get("scripts", {})
        if not sc.get("test"):
            skip("无 test script")
        pm = which("pnpm", "npm")
        if not pm:
            skip("runner 无 pnpm/npm")
        subprocess.run([pm, "install"], cwd=SRC)
        r = subprocess.run([pm, "test"], cwd=SRC)
        if r.returncode != 0:
            fail("单测未通过")
        ok("单测真跑通过")
    skip("非 node 项目 UT 由服务侧 CI 保证")

else:
    fail(f"未知检查项：{check}")
