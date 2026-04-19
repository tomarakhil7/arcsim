# 🎬 ArcSim Demo

## Quick Demo

### 1. Analyze Bad Infrastructure

```bash
cd /Users/a.tomar/Documents/Work/arcsim

# Create file list
cat > test_files.txt << 'DEMO'
examples/kubernetes/bad-ingress.yaml
examples/kubernetes/bad-deployment.yaml
examples/terraform/bad-database.tf
DEMO

# Run ArcSim
./venv/bin/python -m arcsim.main --files test_files.txt
```

**Expected Result:** 6 reliability issues detected:
1. 🔴 Production SPOF (1 replica)
2. 🔴 Missing Readiness Probe
3. 🔴 Database SPOF (no Multi-AZ)
4. 🔴 Timeout Chain #1: Ingress (30s) → API (60s)
5. 🔴 Timeout Chain #2: API (60s) → Database (90s)
6. 🟠 Missing Liveness Probe

---

### 2. Analyze Good Infrastructure

```bash
cat > good_files.txt << 'DEMO'
examples/kubernetes/good-deployment.yaml
DEMO

./venv/bin/python -m arcsim.main --files good_files.txt
```

**Expected Result:** ✅ No reliability issues detected!

---

## What Makes This Demo Impressive

### The Timeout Chain Detection

ArcSim builds a **request flow graph** and detects cascading timeout issues:

```
Request Flow: Ingress → API Service → Database

Timeouts Found:
├─ Ingress (NGINX):     30s  (annotation)
├─ API Service:         60s  (HTTP_TIMEOUT env var)
└─ Database:            90s  (connection string)

Issues Detected:
❌ Ingress timeout < API timeout (30s < 60s)
❌ API timeout < Database timeout (60s < 90s)

Impact:
- Requests terminated upstream while downstream still processing
- Orphaned database operations
- Retry amplification under load
- Common cause of cascading failures
```

**This cross-layer analysis is unique to ArcSim!**

---

## Run All Tests

```bash
# Unit tests
./venv/bin/pytest tests/unit/ -v

# End-to-end test
./venv/bin/python -m arcsim.main --files test_files.txt > /tmp/report.md
grep -c "🔴 Critical" /tmp/report.md  # Should output: 5
```

---

## Try It Yourself

1. Clone/download ArcSim
2. Set up environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the demo above
4. Try it on your own infrastructure!

---

## Share Your Results

If ArcSim catches a real issue in your infrastructure:

1. ⭐ Star the repo
2. Share on Twitter/X with #ArcSim
3. Open a discussion with your story

We want to learn what works and what doesn't!
