# Reusable Workflows

This directory contains reusable GitHub Actions workflows that can be called from other repositories.

## Available Workflows

### 1. go-reusable.yml

Go build and test coverage workflow.

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)
- `go-version` (optional): Go version (default: `1.22`)
- `test-packages` (optional): Packages to test (default: `./...`)

**Secrets:**

- `gh-token` (optional): GitHub token for private repo access

**Example usage:**

```yaml
jobs:
  build:
    uses: opensourceways/agent-development-specification/.github/workflows/go-reusable.yml@main
    with:
      runs-on: ubuntu-latest
      go-version: "1.22"
    secrets:
      gh-token: ${{ secrets.GH_TOKEN }}
```

### 2. sast-reusable.yml

Multi-language SAST scanning (Go, Java, Python, Node.js).

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)
- `go-version` (optional): Go version (default: `1.22`)
- `java-version` (optional): Java version (default: `17`)
- `python-version` (optional): Python version (default: `3.12`)
- `node-version` (optional): Node.js version (default: `20`)

**Secrets:**

- `github-token` (optional): GitHub token

**Example usage:**

```yaml
jobs:
  sast:
    uses: opensourceways/agent-development-specification/.github/workflows/sast-reusable.yml@main
    with:
      runs-on: ubuntu-latest
```

### 3. gitleaks-reusable.yml

GitLeaks secret scanning.

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)

**Secrets:**

- `github-token` (optional): GitHub token
- `gitleaks-license` (optional): License for private repos

**Example usage:**

```yaml
jobs:
  gitleaks:
    uses: opensourceways/agent-development-specification/.github/workflows/gitleaks-reusable.yml@main
    with:
      runs-on: ubuntu-latest
```

### 4. check-branch-naming-reusable.yml

Branch naming convention validation.

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)
- `allowed-prefixes` (optional): Regex pattern for allowed prefixes (default: `^(feature|fix|bugfix|hotfix|release|refactor|chore|docs|test|ci)\/.+$`)

**Example usage:**

```yaml
jobs:
  check-branch-naming:
    uses: opensourceways/agent-development-specification/.github/workflows/check-branch-naming-reusable.yml@main
    with:
      runs-on: ubuntu-latest
```

### 5. trivy-vulnerability-reusable.yml

Trivy vulnerability and secret scanning.

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)
- `scanners` (optional): Scanners to use (default: `vuln,secret`)
- `severity` (optional): Severity levels (default: `UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL`)
- `exit-code` (optional): Exit code when issues found (default: `1`)

**Example usage:**

```yaml
jobs:
  trivy-vulnerability:
    uses: opensourceways/agent-development-specification/.github/workflows/trivy-vulnerability-reusable.yml@main
    with:
      runs-on: ubuntu-latest
```

### 6. trivy-license-reusable.yml

Trivy license scanning.

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)
- `exit-code` (optional): Exit code when issues found (default: `0`)

**Example usage:**

```yaml
jobs:
  trivy-license:
    uses: opensourceways/agent-development-specification/.github/workflows/trivy-license-reusable.yml@main
    with:
      runs-on: ubuntu-latest
```

### 7. document-gate-reusable.yml

Document gate validation for PRs.

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)
- `exempt-labels` (optional): Labels that exempt from check (default: `bug,need_light,task`)

**Example usage:**

```yaml
jobs:
  document-gate:
    uses: opensourceways/agent-development-specification/.github/workflows/document-gate-reusable.yml@main
    with:
      runs-on: ubuntu-latest
```

### 8. check-label-reusable.yml

PR label validation.

**Inputs:**

- `runs-on` (required): Runner to use (default: `ubuntu-latest`)

**Example usage:**

```yaml
jobs:
  check-label:
    uses: opensourceways/agent-development-specification/.github/workflows/check-label-reusable.yml@main
    with:
      runs-on: ubuntu-latest
```

## Runner Selection Guide

For public repositories:

```yaml
with:
  runs-on: ubuntu-latest
```

For private repositories with self-hosted runners:

```yaml
with:
  runs-on: linux-amd64-cpu-4  # For compilation
  runs-on: linux-amd64-cpu-1  # For lightweight checks
```

## Security Best Practices

All workflows use SHA-pinned actions for supply chain security:

- `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd` (v6.0.2)
- `actions/setup-go@40f1582b2485089dde7abd97c1529aa768e1baff` (v5)
- `securego/gosec@4a3bd8af174872c778439083ded7adbf3747e770` (v2.26.1)
- `aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25` (v0.36.0)

## Related Issue

This PR addresses: https://github.com/opensourceways/backlog/issues/367
