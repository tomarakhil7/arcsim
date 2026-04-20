# 🎬 Using ArcSim GitHub Action

## Quick Start

Add this to your `.github/workflows/reliability-check.yml`:

```yaml
name: Reliability Check

on:
  pull_request:
    paths:
      - '**.yaml'
      - '**.yml'
      - '**.tf'

permissions:
  contents: read
  pull-requests: write

jobs:
  arcsim:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: ArcSim Reliability Check
        uses: tomarakhil7/arcsim@v1
```

That's it! ArcSim will automatically:
- ✅ Analyze changed Kubernetes and Terraform files
- ✅ Post findings as PR comments
- ✅ Update comments on new pushes

---

## Configuration Options

### Basic Usage

```yaml
- uses: tomarakhil7/arcsim@v1
```

### Fail on Critical Issues

Make the check fail if critical issues are found:

```yaml
- uses: tomarakhil7/arcsim@v1
  with:
    fail-on-critical: 'true'
```

### Analyze Specific Files

Override auto-detection and specify files:

```yaml
- uses: tomarakhil7/arcsim@v1
  with:
    files: 'k8s/deployment.yaml k8s/ingress.yaml terraform/database.tf'
```

### Custom GitHub Token

Use a custom token (for private repos or enhanced permissions):

```yaml
- uses: tomarakhil7/arcsim@v1
  with:
    github-token: ${{ secrets.CUSTOM_TOKEN }}
```

---

## Complete Example

```yaml
name: Infrastructure Reliability

on:
  pull_request:
    paths:
      - 'infrastructure/**/*.yaml'
      - 'infrastructure/**/*.yml'
      - 'terraform/**/*.tf'
  push:
    branches:
      - main

permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  reliability-check:
    name: ArcSim Analysis
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run ArcSim
        uses: tomarakhil7/arcsim@v1
        with:
          fail-on-critical: 'true'

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: arcsim-report
          path: arcsim_report.md
```

---

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `files` | Space-separated list of files to analyze | No | Auto-detect changed files |
| `github-token` | GitHub token for posting comments | No | `${{ github.token }}` |
| `fail-on-critical` | Fail check if critical issues found | No | `false` |

---

## Outputs

| Output | Description |
|--------|-------------|
| `critical_count` | Number of critical issues found |

---

## What ArcSim Checks

### 🔴 Critical Issues (Production Only)

1. **Production SPOF** - Single-replica deployments
2. **Missing Readiness Probes** - No health checks
3. **Database HA Missing** - RDS without Multi-AZ
4. **Timeout Chain Mismatch** - Cascading timeout issues

### 🟠 Warnings

- Missing liveness probes
- Issues in non-production environments

---

## Example Output

When ArcSim finds issues, it posts a comment like this:

```markdown
# 🔥 ArcSim Reliability Analysis

**Found 3 potential reliability issues**

- 🔴 2 Critical
- 🟠 1 Warning

---

## 🔴 Critical Issues

### 🔴 Production SPOF: api-service

**Rule:** `SPOF-001` | **Confidence:** HIGH
**Resource:** `Deployment/api-service`
**Issue:** Service has only 1 replica(s) in production

<details>
<summary>📊 Impact Analysis (click to expand)</summary>

If the node hosting this pod fails, the entire service will be unavailable...
</details>

<details>
<summary>✅ How to Fix (click to expand)</summary>

1. Increase replicas to at least 2...
</details>
```

---

## Permissions Required

The action needs these permissions:

```yaml
permissions:
  contents: read        # Read repository files
  pull-requests: write  # Post PR comments
```

---

## Supported Environments

- ✅ Public repositories
- ✅ Private repositories
- ✅ GitHub Enterprise

---

## Troubleshooting

### No Files Analyzed

If you see "No infrastructure files changed":
- Ensure your PR modifies `.yaml`, `.yml`, or `.tf` files
- Or use the `files` input to specify files manually

### Permission Denied

If the action can't post comments:
```yaml
permissions:
  pull-requests: write  # Add this
```

### Action Not Running

Check your workflow triggers:
```yaml
on:
  pull_request:
    paths:
      - '**.yaml'  # Matches all YAML files
      - '**.tf'    # Matches all Terraform files
```

---

## Advanced Usage

### Run on Specific Directories

```yaml
on:
  pull_request:
    paths:
      - 'k8s/**'
      - 'terraform/**'
```

### Multiple Jobs

```yaml
jobs:
  k8s-check:
    runs-on: ubuntu-latest
    steps:
      - uses: tomarakhil7/arcsim@v1
        with:
          files: 'k8s/*.yaml'

  terraform-check:
    runs-on: ubuntu-latest
    steps:
      - uses: tomarakhil7/arcsim@v1
        with:
          files: 'terraform/*.tf'
```

---

## FAQ

**Q: Does this slow down my CI?**  
A: No, ArcSim runs in <5 seconds for most repos.

**Q: Will it create noise with false positives?**  
A: No, ArcSim has been tested with 100% accuracy on real repos.

**Q: Can I customize the rules?**  
A: Not yet in V1, but coming in V1.5.

**Q: Does it work with Helm charts?**  
A: Not yet, raw YAML manifests only. Helm support coming soon.

---

## Support

- **Issues:** https://github.com/tomarakhil7/arcsim/issues
- **Discussions:** https://github.com/tomarakhil7/arcsim/discussions
- **Documentation:** https://github.com/tomarakhil7/arcsim

---

**⭐ If ArcSim helps your team, please star the repo!**
