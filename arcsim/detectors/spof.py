"""SPOF (Single Point of Failure) detector"""

from typing import List
from ..models.resource import Deployment
from ..models.finding import Finding


class SPOFDetector:
    """Detect Single Points of Failure in production"""

    RULE_ID = "SPOF-001"

    def check(self, deployment: Deployment, environment: str) -> List[Finding]:
        """Check for SPOF issues

        Args:
            deployment: Kubernetes deployment to check
            environment: Environment name (production, staging, etc)

        Returns:
            List of findings (empty if no issues)
        """
        findings = []

        # Only check production
        if environment != 'production':
            return findings

        # Check replica count
        if deployment.replicas < 2:
            findings.append(Finding(
                severity="CRITICAL",
                rule_id=self.RULE_ID,
                title=f"Production SPOF: {deployment.name}",
                message=f"Service has only {deployment.replicas} replica(s) in production",
                resource_name=deployment.name,
                resource_kind=deployment.kind,
                impact=(
                    "If the node hosting this pod fails, the entire service will be unavailable. "
                    "This represents a Single Point of Failure (SPOF) that can cause complete outages.\n\n"
                    "**Consequences:**\n"
                    "- Service downtime during node failures\n"
                    "- No redundancy during deployments\n"
                    "- Cannot handle maintenance or updates without downtime\n"
                    "- Vulnerability to pod crashes or OOM kills"
                ),
                mitigation=(
                    "**Recommended Actions:**\n\n"
                    "1. Increase replicas to at least 2 for redundancy:\n"
                    "   ```yaml\n"
                    "   spec:\n"
                    "     replicas: 3  # or more based on load\n"
                    "   ```\n\n"
                    "2. Add PodDisruptionBudget to prevent all pods from being evicted:\n"
                    "   ```yaml\n"
                    "   apiVersion: policy/v1\n"
                    "   kind: PodDisruptionBudget\n"
                    "   metadata:\n"
                    f"     name: {deployment.name}-pdb\n"
                    "   spec:\n"
                    "     minAvailable: 1\n"
                    "     selector:\n"
                    "       matchLabels:\n"
                    f"         app: {deployment.name}\n"
                    "   ```\n\n"
                    "3. Use anti-affinity to spread pods across nodes/zones:\n"
                    "   ```yaml\n"
                    "   spec:\n"
                    "     template:\n"
                    "       spec:\n"
                    "         affinity:\n"
                    "           podAntiAffinity:\n"
                    "             preferredDuringSchedulingIgnoredDuringExecution:\n"
                    "             - weight: 100\n"
                    "               podAffinityTerm:\n"
                    "                 topologyKey: kubernetes.io/hostname\n"
                    "   ```"
                ),
                confidence="HIGH"
            ))

        return findings
