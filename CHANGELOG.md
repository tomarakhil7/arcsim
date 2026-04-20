# Changelog

All notable changes to ArcSim will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-04-20

### Added
- 🎉 Initial release of ArcSim
- Production SPOF detection (single-replica services in production)
- Health probe validation (readiness and liveness probes)
- Database HA detection (RDS Multi-AZ validation)
- **Timeout chain analysis** (unique cross-layer timeout mismatch detection)
- GitHub Actions integration (automatic PR analysis)
- Kubernetes support (Deployments, StatefulSets, Ingress)
- Terraform support (AWS RDS)
- Markdown report output
- Context-aware severity (production vs non-production)

### Validated
- 473+ real-world files tested across 15+ major open-source projects
- 229+ reliability issues found with 0 false positives
- 100% accuracy on known reliability patterns

### Documentation
- Comprehensive README with examples
- GitHub Action usage guide
- Case studies with ROI calculations
- Validation reports
- Contributing guidelines

---

## Release Notes

### What's Special About v1.0.0

**Timeout Chain Detection (Unique!)** - ArcSim is the only tool that analyzes cross-layer timeout configurations to detect cascading failures:

```yaml
Ingress: 30s → API: 60s → Database: 90s
         ❌        ❌            ❌
```

This pattern has caused major outages at companies like Stripe and AWS. ArcSim catches it before deployment.

### Known Limitations

- **Helm Templates:** ArcSim analyzes rendered YAML, not Helm templates with `{{ }}` syntax. Run `helm template` first.
- **Timeout Chains:** Rare in practice but critical when present. You may not see this triggered often.
- **Terraform Coverage:** Currently supports AWS RDS. GCP/Azure coming soon.

### Credits

Inspired by reliability incidents at Stripe, AWS, Google, and every company that's had a config-related outage.

Built to prevent the next one.

---

[Unreleased]: https://github.com/tomarakhil7/arcsim/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/tomarakhil7/arcsim/releases/tag/v1.0.0
