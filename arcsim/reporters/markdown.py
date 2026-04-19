"""Markdown report generator"""

from typing import List
from ..models.finding import Finding


class MarkdownReporter:
    """Generate markdown reports"""

    def generate(self, findings: List[Finding]) -> str:
        """Generate markdown report from findings

        Args:
            findings: List of Finding objects

        Returns:
            Formatted markdown string
        """
        if not findings:
            return self._generate_success_report()

        # Sort by severity
        critical = [f for f in findings if f.severity == "CRITICAL"]
        warnings = [f for f in findings if f.severity == "WARNING"]

        report = "# 🔥 ArcSim Reliability Analysis\n\n"
        report += f"**Found {len(findings)} potential reliability issue{'s' if len(findings) != 1 else ''}**\n\n"
        report += f"- 🔴 {len(critical)} Critical\n"
        report += f"- 🟠 {len(warnings)} Warning{'s' if len(warnings) != 1 else ''}\n\n"
        report += "---\n\n"

        if critical:
            report += "## 🔴 Critical Issues\n\n"
            report += "These issues can cause production outages and should be addressed immediately.\n\n"
            for finding in critical:
                report += self._format_finding(finding)

        if warnings:
            report += "## 🟠 Warnings\n\n"
            report += "These issues should be addressed to improve reliability.\n\n"
            for finding in warnings:
                report += self._format_finding(finding)

        report += "\n---\n\n"
        report += "**About ArcSim**\n\n"
        report += "ArcSim prevents fragile infrastructure changes from reaching production by detecting "
        report += "reliability risks before deployment. It analyzes Kubernetes manifests and Terraform files "
        report += "to catch common outage patterns.\n\n"
        report += "*Analyzed by [ArcSim](https://github.com/yourusername/arcsim) - "
        report += "Reliability guardrails for infrastructure*\n"

        return report

    def _format_finding(self, finding: Finding) -> str:
        """Format a single finding

        Args:
            finding: Finding object

        Returns:
            Formatted markdown string
        """
        emoji = "🔴" if finding.severity == "CRITICAL" else "🟠"

        report = f"### {emoji} {finding.title}\n\n"
        report += f"**Rule:** `{finding.rule_id}` | **Confidence:** {finding.confidence}\n\n"
        report += f"**Resource:** `{finding.resource_kind}/{finding.resource_name}`\n\n"
        report += f"**Issue:** {finding.message}\n\n"

        report += f"<details>\n"
        report += f"<summary><strong>📊 Impact Analysis</strong> (click to expand)</summary>\n\n"
        report += f"{finding.impact}\n\n"
        report += f"</details>\n\n"

        report += f"<details>\n"
        report += f"<summary><strong>✅ How to Fix</strong> (click to expand)</summary>\n\n"
        report += f"{finding.mitigation}\n\n"
        report += f"</details>\n\n"

        report += "---\n\n"

        return report

    def _generate_success_report(self) -> str:
        """Generate success report when no issues found

        Returns:
            Formatted markdown string
        """
        return """# ✅ ArcSim Reliability Analysis

**No reliability issues detected!**

Your infrastructure changes look good from a reliability perspective. All checks passed:

- ✅ No Single Points of Failure in production
- ✅ Health probes configured
- ✅ Database high availability enabled
- ✅ No timeout chain mismatches

---

*Analyzed by [ArcSim](https://github.com/yourusername/arcsim) - Reliability guardrails for infrastructure*
"""
