"""Kubernetes YAML parser"""

import yaml
from typing import List, Dict
from ..models.resource import KubernetesResource, Deployment, Ingress


class KubernetesParser:
    """Parse Kubernetes YAML manifests"""

    def parse_file(self, filepath: str) -> List[KubernetesResource]:
        """Parse a K8s YAML file (may contain multiple resources)

        Args:
            filepath: Path to YAML file

        Returns:
            List of parsed Kubernetes resources
        """
        resources = []

        with open(filepath, 'r') as f:
            # YAML files can have multiple documents separated by ---
            for doc in yaml.safe_load_all(f):
                if doc is None:
                    continue

                resource = self._parse_resource(doc)
                if resource:
                    resources.append(resource)

        return resources

    def _parse_resource(self, doc: Dict) -> KubernetesResource:
        """Convert YAML dict to resource object

        Args:
            doc: Parsed YAML document

        Returns:
            KubernetesResource subclass instance
        """
        kind = doc.get('kind')

        if kind in ['Deployment', 'StatefulSet']:
            return Deployment.from_k8s(doc)
        elif kind == 'Ingress':
            return Ingress.from_k8s(doc)
        else:
            # Generic resource
            metadata = doc.get('metadata', {})
            return KubernetesResource(
                kind=kind or 'Unknown',
                name=metadata.get('name', 'unknown'),
                namespace=metadata.get('namespace'),
                raw=doc
            )

    def get_environment(self, resource: KubernetesResource) -> str:
        """Infer environment from labels/namespace

        Args:
            resource: Kubernetes resource

        Returns:
            Environment string: 'production', 'staging', or 'unknown'
        """
        # Check namespace
        if resource.namespace:
            ns_lower = resource.namespace.lower()
            if 'prod' in ns_lower:
                return 'production'
            elif 'staging' in ns_lower or 'stage' in ns_lower:
                return 'staging'

        # Check labels
        labels = resource.raw.get('metadata', {}).get('labels', {})
        env = labels.get('environment', labels.get('env', ''))

        if env:
            env_lower = str(env).lower()
            if env_lower in ['prod', 'production']:
                return 'production'
            elif env_lower in ['staging', 'stage']:
                return 'staging'

        return 'unknown'
