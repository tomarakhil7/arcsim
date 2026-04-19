"""Timeout extraction from various sources"""

from typing import List
import re
from ..models.resource import Ingress, Deployment
from ..models.timeout import Timeout, parse_duration


class TimeoutExtractor:
    """Extract timeout configurations from various sources"""

    def extract_from_nginx_ingress(self, ingress: Ingress) -> List[Timeout]:
        """Extract timeouts from NGINX Ingress annotations

        Args:
            ingress: Ingress resource

        Returns:
            List of Timeout objects
        """
        timeouts = []

        annotations = ingress.annotations

        # Common NGINX timeout annotations
        timeout_annotations = {
            'nginx.ingress.kubernetes.io/proxy-read-timeout': 'read',
            'nginx.ingress.kubernetes.io/proxy-send-timeout': 'send',
            'nginx.ingress.kubernetes.io/proxy-connect-timeout': 'connect',
        }

        for annotation, timeout_type in timeout_annotations.items():
            if annotation in annotations:
                raw_value = annotations[annotation]
                seconds = parse_duration(raw_value)

                if seconds:
                    timeouts.append(Timeout(
                        source='nginx-ingress',
                        resource_name=f"{ingress.name}:{timeout_type}",
                        value_seconds=seconds,
                        raw_value=str(raw_value),
                        location=f"Ingress/{ingress.name} annotation {annotation}"
                    ))

        return timeouts

    def extract_from_deployment(self, deployment: Deployment) -> List[Timeout]:
        """Extract timeouts from deployment env vars

        Args:
            deployment: Deployment resource

        Returns:
            List of Timeout objects
        """
        timeouts = []

        # Common timeout env var patterns
        timeout_patterns = [
            'HTTP_TIMEOUT',
            'REQUEST_TIMEOUT',
            'API_TIMEOUT',
            'TIMEOUT',
            'SERVER_TIMEOUT',
            'CLIENT_TIMEOUT'
        ]

        for var_name, var_value in deployment.env_vars.items():
            if any(pattern in var_name.upper() for pattern in timeout_patterns):
                seconds = parse_duration(var_value)

                # If it's a large number (>1000) and no unit specified, likely milliseconds
                if seconds and seconds > 1000 and var_value.isdigit():
                    seconds = seconds // 1000

                if seconds:
                    timeouts.append(Timeout(
                        source='deployment-env',
                        resource_name=f"{deployment.name}:{var_name}",
                        value_seconds=seconds,
                        raw_value=str(var_value),
                        location=f"Deployment/{deployment.name} env.{var_name}"
                    ))

        return timeouts

    def extract_from_connection_string(self, conn_str: str, resource_name: str) -> List[Timeout]:
        """Extract timeout from database connection string

        Args:
            conn_str: Database connection string
            resource_name: Name of the resource for reporting

        Returns:
            List of Timeout objects
        """
        timeouts = []

        # PostgreSQL patterns
        # postgresql://user:pass@host:5432/db?connect_timeout=10
        if 'connect_timeout=' in conn_str:
            match = re.search(r'connect_timeout=(\d+)', conn_str)
            if match:
                seconds = int(match.group(1))
                timeouts.append(Timeout(
                    source='db-connection',
                    resource_name=resource_name,
                    value_seconds=seconds,
                    raw_value=f"{seconds}s",
                    location=f"Connection string connect_timeout parameter"
                ))

        # MySQL patterns
        # mysql://user:pass@host:3306/db?connectTimeout=10000
        if 'connectTimeout=' in conn_str:
            match = re.search(r'connectTimeout=(\d+)', conn_str)
            if match:
                milliseconds = int(match.group(1))
                seconds = milliseconds // 1000
                timeouts.append(Timeout(
                    source='db-connection',
                    resource_name=resource_name,
                    value_seconds=seconds,
                    raw_value=f"{milliseconds}ms",
                    location=f"Connection string connectTimeout parameter"
                ))

        return timeouts

    def extract_from_deployment_db_refs(self, deployment: Deployment) -> List[Timeout]:
        """Look for database connection strings in deployment env vars

        Args:
            deployment: Deployment resource

        Returns:
            List of Timeout objects
        """
        timeouts = []

        db_url_patterns = ['DATABASE_URL', 'DB_URL', 'POSTGRES_URL', 'MYSQL_URL', 'MONGODB_URI']

        for var_name, var_value in deployment.env_vars.items():
            if any(pattern in var_name.upper() for pattern in db_url_patterns):
                timeouts.extend(
                    self.extract_from_connection_string(var_value, f"{deployment.name}-db")
                )

        return timeouts
