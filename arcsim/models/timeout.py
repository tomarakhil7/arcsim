"""Timeout models and parsing utilities"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Timeout:
    """Represents a timeout configuration"""

    source: str  # "nginx-ingress", "deployment-env", "rds-connection"
    resource_name: str
    value_seconds: int
    raw_value: str
    location: str  # Where it was found


def parse_duration(duration_str: str) -> Optional[int]:
    """Parse duration string to seconds

    Supports: "30s", "30", "5m", "1h", "30000ms"

    Args:
        duration_str: Duration string to parse

    Returns:
        Duration in seconds, or None if cannot parse

    Examples:
        >>> parse_duration("30s")
        30
        >>> parse_duration("5m")
        300
        >>> parse_duration("30000")
        30000
        >>> parse_duration("30000ms")
        30
    """
    if not duration_str:
        return None

    duration_str = str(duration_str).strip().lower()

    # Empty string
    if not duration_str:
        return None

    # Plain number (assume seconds)
    if duration_str.isdigit():
        return int(duration_str)

    # Milliseconds
    if duration_str.endswith('ms'):
        try:
            return int(duration_str[:-2]) // 1000
        except ValueError:
            return None

    # Seconds
    if duration_str.endswith('s'):
        try:
            return int(duration_str[:-1])
        except ValueError:
            return None

    # Minutes
    if duration_str.endswith('m'):
        try:
            return int(duration_str[:-1]) * 60
        except ValueError:
            return None

    # Hours
    if duration_str.endswith('h'):
        try:
            return int(duration_str[:-1]) * 3600
        except ValueError:
            return None

    return None
