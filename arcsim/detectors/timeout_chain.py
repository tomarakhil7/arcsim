"""Timeout chain mismatch detector"""

from typing import List
from ..models.finding import Finding
from ..graph.builder import RequestFlowGraph


class TimeoutChainDetector:
    """Detect timeout mismatches across request paths"""

    RULE_ID = "TIMEOUT-CHAIN-001"

    def check(self, graph: RequestFlowGraph) -> List[Finding]:
        """Check for timeout chain mismatches

        Args:
            graph: Request flow graph with timeout information

        Returns:
            List of findings
        """
        findings = []

        paths = graph.get_request_paths()

        for path in paths:
            # Extract timeouts from path
            timeouts_in_path = []
            for node in path:
                if node.timeout:
                    timeouts_in_path.append((node, node.timeout))

            # Check for mismatches (upstream should be > downstream)
            for i in range(len(timeouts_in_path) - 1):
                upstream_node, upstream_timeout = timeouts_in_path[i]
                downstream_node, downstream_timeout = timeouts_in_path[i + 1]

                if upstream_timeout.value_seconds < downstream_timeout.value_seconds:
                    # Calculate the path for display
                    path_display = ' → '.join(n.name.replace('ingress:', '').replace('service:', '').replace('database:', '') for n in path)

                    findings.append(Finding(
                        severity="CRITICAL",
                        rule_id=self.RULE_ID,
                        title="Timeout Chain Mismatch Detected",
                        message=(
                            f"Upstream timeout ({upstream_timeout.value_seconds}s) "
                            f"< downstream timeout ({downstream_timeout.value_seconds}s)"
                        ),
                        resource_name=f"{upstream_node.name} → {downstream_node.name}",
                        resource_kind="TimeoutChain",
                        impact=(
                            f"**Request Flow Path:**\n"
                            f"`{path_display}`\n\n"
                            f"**Timeout Configuration:**\n"
                            f"- **{upstream_node.name.replace('ingress:', '').replace('service:', '')}**: "
                            f"{upstream_timeout.value_seconds}s\n"
                            f"  - Location: {upstream_timeout.location}\n"
                            f"  - Raw value: `{upstream_timeout.raw_value}`\n\n"
                            f"- **{downstream_node.name.replace('service:', '').replace('database:', '')}**: "
                            f"{downstream_timeout.value_seconds}s\n"
                            f"  - Location: {downstream_timeout.location}\n"
                            f"  - Raw value: `{downstream_timeout.raw_value}`\n\n"
                            f"**Why This is Critical:**\n\n"
                            f"Requests will be terminated at the upstream layer "
                            f"(**{upstream_node.name.replace('ingress:', '').replace('service:', '')}**) "
                            f"after {upstream_timeout.value_seconds}s, "
                            f"but the downstream layer "
                            f"(**{downstream_node.name.replace('service:', '').replace('database:', '')}**) "
                            f"will continue processing for up to {downstream_timeout.value_seconds}s.\n\n"
                            f"**Consequences:**\n\n"
                            f"1. **Wasted Resources** - Backend continues work on abandoned requests, consuming CPU/memory\n"
                            f"2. **Orphaned Operations** - Database writes complete but client never sees result\n"
                            f"3. **Retry Amplification** - Clients retry while backend still processing, multiplying load by {downstream_timeout.value_seconds // upstream_timeout.value_seconds}×\n"
                            f"4. **Cascading Failures** - Under high load, this pattern causes system-wide outages\n"
                            f"5. **Resource Exhaustion** - Connection pools fill up with zombie connections\n\n"
                            f"**Real-World Impact:**\n\n"
                            f"This exact pattern has caused major outages at companies like Stripe, AWS, and others. "
                            f"It's a common root cause of production incidents that are hard to debug."
                        ),
                        mitigation=(
                            f"**Option 1 (Recommended): Reduce Downstream Timeout**\n\n"
                            f"Set the downstream timeout to less than {upstream_timeout.value_seconds}s to ensure operations "
                            f"complete before upstream timeout:\n\n"
                            f"```\n"
                            f"Recommended: {max(upstream_timeout.value_seconds - 5, upstream_timeout.value_seconds // 2)}s "
                            f"(gives {min(5, upstream_timeout.value_seconds // 2)}s safety margin)\n"
                            f"```\n\n"
                            f"**Option 2: Increase Upstream Timeout**\n\n"
                            f"Set the upstream timeout to more than {downstream_timeout.value_seconds}s:\n\n"
                            f"```\n"
                            f"Recommended: {downstream_timeout.value_seconds + 10}s "
                            f"(gives 10s safety margin)\n"
                            f"```\n\n"
                            f"**Best Practice Guidelines:**\n\n"
                            f"Each layer should have timeout < upstream timeout, with 10-20% buffer:\n\n"
                            f"```\n"
                            f"Good Example:\n"
                            f"  Load Balancer:  30s\n"
                            f"  API Service:    25s  (83% of LB timeout)\n"
                            f"  Database:       20s  (80% of API timeout)\n\n"
                            f"Bad Example (current):\n"
                            f"  {upstream_node.name.replace('ingress:', '').replace('service:', ''):20s} {upstream_timeout.value_seconds}s\n"
                            f"  {downstream_node.name.replace('service:', '').replace('database:', ''):20s} {downstream_timeout.value_seconds}s  ❌\n"
                            f"```\n\n"
                            f"**How to Fix:**\n\n"
                            f"1. Update {downstream_timeout.location}\n"
                            f"2. Test thoroughly in staging\n"
                            f"3. Monitor p99 latency to ensure operations complete within new timeout\n"
                            f"4. Consider adding request deadline propagation"
                        ),
                        confidence="HIGH"
                    ))

        return findings
