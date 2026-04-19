"""Finding model for representing reliability issues"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Finding:
    """Represents a reliability issue found during analysis"""

    severity: str  # CRITICAL, WARNING, INFO
    rule_id: str
    title: str
    message: str
    resource_name: str
    resource_kind: str
    impact: str
    mitigation: str
    confidence: str  # HIGH, MEDIUM, LOW

    def __str__(self):
        emoji = "🔴" if self.severity == "CRITICAL" else "🟠" if self.severity == "WARNING" else "🔵"
        return f"{emoji} {self.severity}: {self.title}"
