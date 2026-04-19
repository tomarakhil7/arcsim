"""Database High Availability detector"""

from typing import List, Dict
from ..models.finding import Finding


class DatabaseHADetector:
    """Detect databases without high availability"""

    RULE_ID = "DB-HA-001"

    def check(self, resource: Dict, environment: str) -> List[Finding]:
        """Check for database HA issues

        Args:
            resource: Terraform resource dict
            environment: Environment name (production, staging, etc)

        Returns:
            List of findings (empty if no issues)
        """
        findings = []

        # Only check production
        if environment != 'production':
            return findings

        # Check AWS RDS
        if resource['type'] == 'aws_db_instance':
            config = resource['config']

            # multi_az can be a boolean or list with boolean
            multi_az = config.get('multi_az', [False])
            if isinstance(multi_az, list):
                multi_az = multi_az[0] if multi_az else False

            if not multi_az:
                findings.append(Finding(
                    severity="CRITICAL",
                    rule_id=self.RULE_ID,
                    title=f"Database SPOF: {resource['name']}",
                    message="RDS instance has Multi-AZ disabled in production",
                    resource_name=resource['name'],
                    resource_kind='aws_db_instance',
                    impact=(
                        "If the primary Availability Zone fails, the database will be completely unavailable.\n\n"
                        "**Expected Impact:**\n"
                        "- Complete data access outage\n"
                        "- Manual failover required (hours of downtime)\n"
                        "- All services depending on this database will fail\n"
                        "- No automatic recovery from AZ-level failures\n"
                        "- Maintenance operations require downtime\n\n"
                        "**Historical Precedent:**\n"
                        "AWS AZ failures have caused major outages for companies running single-AZ databases. "
                        "Multi-AZ is the minimum requirement for production databases."
                    ),
                    mitigation=(
                        "**Enable Multi-AZ for automatic failover:**\n\n"
                        "```hcl\n"
                        "resource \"aws_db_instance\" \"main\" {\n"
                        "  # ... existing config ...\n"
                        "  \n"
                        "  multi_az = true  # Enable this\n"
                        "  \n"
                        "  # Recommended: Also set backup retention\n"
                        "  backup_retention_period = 7\n"
                        "  \n"
                        "  # Recommended: Enable automated backups\n"
                        "  backup_window = \"03:00-04:00\"\n"
                        "}\n"
                        "```\n\n"
                        "**Important Notes:**\n"
                        "- Enabling Multi-AZ requires a reboot (brief downtime)\n"
                        "- Multi-AZ approximately doubles the cost\n"
                        "- Failover typically takes 60-120 seconds\n"
                        "- This is essential for production workloads\n\n"
                        "**Alternative (not recommended for production):**\n"
                        "If you truly cannot afford Multi-AZ:\n"
                        "- Set up manual backup/restore procedures\n"
                        "- Document RTO (Recovery Time Objective)\n"
                        "- Have tested restore playbooks\n"
                        "- Accept the risk of extended downtime"
                    ),
                    confidence="HIGH"
                ))

        return findings
