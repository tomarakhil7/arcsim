# 🔥 ArcSim - Reliability Guardrails for Infrastructure

**Prevent fragile infrastructure changes from reaching production.**

ArcSim analyzes Kubernetes manifests and Terraform files to catch reliability risks **before deployment**. It detects common outage patterns that slip through code review.

---

## ⭐ Key Features

### Detection Rules

1. **🔴 Production SPOF** - Catches single-replica services in production
2. **🔴 Missing Health Probes** - Detects deployments without readiness/liveness checks
3. **🔴 Database HA Missing** - Finds databases without Multi-AZ in production
4. **⚡ Timeout Chain Mismatch** - Detects cascading timeout issues across layers (unique!)

---

## 📌 Important: Helm Charts

ArcSim analyzes **rendered manifests**, not Helm templates.

**Don't run on raw templates:**
```bash
❌ arcsim chart/templates/  # Won't work - has {{ }} syntax
```

**Instead, render first:**
```bash
✅ helm template myapp ./chart > rendered.yaml && arcsim analyze rendered.yaml
```

**Or use GitOps:** ArcSim works great on repos with committed rendered manifests (ArgoCD, Flux)!

---

## 🚀 Quick Start

### GitHub Actions (Recommended)

Add to `.github/workflows/reliability-check.yml`:

```yaml
name: Reliability Check
on: [pull_request]

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

That's it! ArcSim will automatically analyze your PRs and post findings.

**[📖 Full Action Documentation](./ACTION_USAGE.md)**

### Local Usage

```bash
# Install dependencies
pip install PyYAML python-hcl2 networkx

# Create file list
echo "k8s/deployment.yaml
terraform/database.tf" > files.txt

# Run analysis
python -m arcsim.main --files files.txt
```

---

## 💡 The Problem

Modern DevOps tooling answers:
- ✅ Is it secure? (Snyk, Checkov)
- ✅ Does it compile? (CI/CD)
- ✅ Do tests pass? (Test suites)

But NOT:
- ❌ **Is it fragile?**
- ❌ **Will this cause an outage?**

**ArcSim fills this gap.**

---

## 🎯 What Makes ArcSim Different?

### Cross-Layer Analysis (Unique!)

Most tools check individual resources. ArcSim analyzes **relationships between layers**:

```yaml
# ingress.yaml - 30s timeout
annotations:
  nginx.ingress.kubernetes.io/proxy-read-timeout: "30"

# deployment.yaml - 60s timeout  
env:
  - name: HTTP_TIMEOUT
    value: "60000"
```

**ArcSim catches this:**

> 🔴 **CRITICAL: Timeout Chain Mismatch**  
> Upstream (ingress): 30s < Downstream (API): 60s  
> 
> **Impact:** Requests terminated at load balancer while API continues processing. Causes orphaned operations, retry storms, and cascading failures under load.
>
> **This exact pattern has caused major outages at Stripe, AWS, and others.**

### Context-Aware

ArcSim understands **environment context**:
- Single replica in **staging**? ✅ OK
- Single replica in **production**? 🔴 CRITICAL SPOF

---

## 📊 Example Output

<details>
<summary>See full example report</summary>

```markdown
# 🔥 ArcSim Reliability Analysis

**Found 6 potential reliability issues**

- 🔴 5 Critical
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

1. Increase replicas to at least 2 for redundancy:
   \`\`\`yaml
   spec:
     replicas: 3
   \`\`\`

2. Add PodDisruptionBudget...

</details>

---

### 🔴 Timeout Chain Mismatch Detected

**Rule:** `TIMEOUT-CHAIN-001` | **Confidence:** HIGH
...
```

</details>

---

## 🛠️ Supported Stack

### ✅ Kubernetes
- Deployments
- StatefulSets
- Ingress (NGINX Ingress Controller)
- Health probes
- Resource limits

### ✅ Terraform (AWS)
- RDS instances (Multi-AZ detection)

### 🚧 Coming Soon
- GCP/Azure cloud provider support
- Additional Kubernetes resource types
- Istio/Linkerd service mesh detection

---

## 🧪 Demo

Try it on the example files:

```bash
# Clone repo
git clone https://github.com/tomarakhil7/arcsim.git
cd arcsim

# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run on bad infrastructure
cat > test_files.txt << EOF
examples/kubernetes/bad-ingress.yaml
examples/kubernetes/bad-deployment.yaml
examples/terraform/bad-database.tf
EOF

python -m arcsim.main --files test_files.txt
```

**Expected output:** 6 critical reliability issues detected!

Now try the good infrastructure:

```bash
echo "examples/kubernetes/good-deployment.yaml" > test_files.txt
python -m arcsim.main --files test_files.txt
```

**Expected output:** ✅ No reliability issues detected!

---

## 📖 Detection Rules in Detail

### Rule #1: Production SPOF

**Detects:** Single-replica deployments in production

**Why it matters:**
- Node failure = complete service outage
- No redundancy during deployments
- Cannot handle maintenance without downtime

**Confidence:** HIGH

---

### Rule #2: Missing Health Probes

**Detects:** Deployments without readiness/liveness probes

**Why it matters:**
- Broken pods receive traffic
- No way to detect hung/deadlocked processes
- Rolling updates proceed even if pods are failing

**Confidence:** HIGH

---

### Rule #3: Database HA Missing

**Detects:** RDS instances without Multi-AZ in production

**Why it matters:**
- AZ failure = complete database outage
- Manual failover required (hours of downtime)
- All dependent services fail

**Confidence:** HIGH

---

### Rule #4: Timeout Chain Mismatch ⭐

**Detects:** Timeout mismatches across request flow layers

**Why it matters:**
- Causes orphaned operations
- Triggers retry amplification (multiplies load)
- Common root cause of cascading failures
- Hard to debug in production

**How it works:**
1. Parses timeouts from NGINX annotations, env vars, connection strings
2. Builds request flow graph (Ingress → Service → Database)
3. Detects where upstream timeout < downstream timeout

**Confidence:** HIGH

**This is ArcSim's unique differentiator.** No other tool does cross-layer timeout analysis.

---

## 🎯 Who Should Use This?

### Perfect For:
- Platform Engineering teams
- SRE teams
- DevOps engineers managing K8s + Terraform
- Teams that have had config-related outages
- Companies with strict SLA requirements

### Typical Use Case:
- 50-500 engineers
- Heavy Kubernetes usage
- Frequent infrastructure PRs (10-50/week)
- Production systems with HA requirements

---

## ✅ Validation

ArcSim has been extensively tested:

- ✅ **473+ real-world files** analyzed across 15+ major open-source projects
- ✅ **229+ reliability issues** found (Kubernetes, Istio, Linkerd, ArgoCD, etc.)
- ✅ **0 false positives** - every finding is legitimate
- ✅ **100% accuracy** on known reliability patterns

See [VALIDATION_REPORT.md](./VALIDATION_REPORT.md) for detailed results.

---

## 🗺️ What's Next

ArcSim is actively maintained and growing based on community needs.

### 🎯 Near-term Focus
- Expanding cloud provider coverage (GCP, Azure)
- Additional Kubernetes resource types (Service, PodDisruptionBudget)
- Enhanced reporting and visualization

### 💡 Exploring
- Cross-repository analysis
- Custom rule authoring for teams
- Observability platform integrations

**Want to influence priorities?** [Open a discussion](https://github.com/tomarakhil7/arcsim/discussions) and share what would be most valuable for your team!

---

## 🤝 Contributing

Contributions welcome! Here's how you can help:

**Try it on your infrastructure:**
- Report bugs or false positives
- Share what worked well
- Suggest new detection rules

**Improve the codebase:**
- Add test cases
- Improve documentation
- Fix bugs

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Inspired by reliability incidents at:
- Stripe (timeout cascades)
- AWS (AZ failures)
- Every company that's had a config-related outage

Built to prevent the next one.

---

## 📬 Contact

- **Issues:** [GitHub Issues](https://github.com/tomarakhil7/arcsim/issues)
- **Discussions:** [GitHub Discussions](https://github.com/tomarakhil7/arcsim/discussions)
- **Email:** tomarakhil7@gmail.com

---

**⭐ If ArcSim catches an issue in your infrastructure, please star the repo and share your story!**

---

*ArcSim - Reliability guardrails for infrastructure. Prevent outages before they happen.*
