"""Health probe detector"""

from typing import List
from ..models.resource import Deployment
from ..models.finding import Finding


class HealthProbeDetector:
    """Detect missing health probes"""

    READINESS_RULE_ID = "HEALTH-001"
    LIVENESS_RULE_ID = "HEALTH-002"

    def check(self, deployment: Deployment, environment: str) -> List[Finding]:
        """Check for missing health probes

        Args:
            deployment: Kubernetes deployment to check
            environment: Environment name (production, staging, etc)

        Returns:
            List of findings (empty if no issues)
        """
        findings = []

        # Check readiness probe
        if not deployment.has_readiness_probe:
            severity = "CRITICAL" if environment == "production" else "WARNING"
            findings.append(Finding(
                severity=severity,
                rule_id=self.READINESS_RULE_ID,
                title=f"Missing Readiness Probe: {deployment.name}",
                message="No readinessProbe configured",
                resource_name=deployment.name,
                resource_kind=deployment.kind,
                impact=(
                    "Without a readiness probe, Kubernetes cannot determine if the pod is ready to serve traffic.\n\n"
                    "**Consequences:**\n"
                    "- Broken pods will receive traffic during deployment\n"
                    "- Users will experience errors and timeouts\n"
                    "- Rolling updates may proceed even if new pods are failing\n"
                    "- Load balancers will route traffic to unhealthy instances\n"
                    "- No way to gracefully handle application startup time"
                ),
                mitigation=(
                    "**Add a readinessProbe** that checks your application's health endpoint:\n\n"
                    "```yaml\n"
                    "spec:\n"
                    "  template:\n"
                    "    spec:\n"
                    "      containers:\n"
                    "      - name: app\n"
                    "        readinessProbe:\n"
                    "          httpGet:\n"
                    "            path: /health\n"
                    "            port: 8080\n"
                    "          initialDelaySeconds: 5\n"
                    "          periodSeconds: 10\n"
                    "          timeoutSeconds: 3\n"
                    "          successThreshold: 1\n"
                    "          failureThreshold: 3\n"
                    "```\n\n"
                    "**For non-HTTP services:**\n"
                    "```yaml\n"
                    "readinessProbe:\n"
                    "  tcpSocket:\n"
                    "    port: 8080\n"
                    "  initialDelaySeconds: 5\n"
                    "  periodSeconds: 10\n"
                    "```\n\n"
                    "**Or use exec:**\n"
                    "```yaml\n"
                    "readinessProbe:\n"
                    "  exec:\n"
                    "    command:\n"
                    "    - /bin/sh\n"
                    "    - -c\n"
                    "    - /health-check.sh\n"
                    "```"
                ),
                confidence="HIGH"
            ))

        # Check liveness probe
        if not deployment.has_liveness_probe:
            severity = "WARNING"  # Less critical than readiness
            findings.append(Finding(
                severity=severity,
                rule_id=self.LIVENESS_RULE_ID,
                title=f"Missing Liveness Probe: {deployment.name}",
                message="No livenessProbe configured",
                resource_name=deployment.name,
                resource_kind=deployment.kind,
                impact=(
                    "Without a liveness probe, Kubernetes cannot detect if the application has deadlocked.\n\n"
                    "**Consequences:**\n"
                    "- Hung pods will continue serving traffic indefinitely\n"
                    "- Memory leaks won't trigger pod restarts\n"
                    "- Application deadlocks will persist\n"
                    "- No automatic recovery from unresponsive states"
                ),
                mitigation=(
                    "**Add a livenessProbe** to restart unhealthy pods:\n\n"
                    "```yaml\n"
                    "spec:\n"
                    "  template:\n"
                    "    spec:\n"
                    "      containers:\n"
                    "      - name: app\n"
                    "        livenessProbe:\n"
                    "          httpGet:\n"
                    "            path: /health\n"
                    "            port: 8080\n"
                    "          initialDelaySeconds: 30  # Higher than readiness\n"
                    "          periodSeconds: 30\n"
                    "          timeoutSeconds: 5\n"
                    "          successThreshold: 1\n"
                    "          failureThreshold: 3\n"
                    "```\n\n"
                    "**Important:** Set `initialDelaySeconds` higher than readiness probe to avoid restart loops during startup."
                ),
                confidence="HIGH"
            ))

        return findings
