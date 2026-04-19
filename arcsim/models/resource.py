"""Resource models for Kubernetes and Terraform"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any


@dataclass
class KubernetesResource:
    """Base Kubernetes resource"""

    kind: str
    name: str
    namespace: Optional[str]
    raw: Dict

    @property
    def is_deployment(self) -> bool:
        return self.kind in ['Deployment', 'StatefulSet']

    @property
    def is_ingress(self) -> bool:
        return self.kind == 'Ingress'


@dataclass
class Deployment(KubernetesResource):
    """Kubernetes Deployment or StatefulSet"""

    replicas: int
    env_vars: Dict[str, str]
    annotations: Dict[str, str]
    has_readiness_probe: bool
    has_liveness_probe: bool

    @classmethod
    def from_k8s(cls, k8s_dict: Dict):
        """Create Deployment from parsed K8s YAML"""
        spec = k8s_dict.get('spec', {})
        template = spec.get('template', {})
        metadata = k8s_dict.get('metadata', {})

        # Get first container
        containers = template.get('spec', {}).get('containers', [])
        container = containers[0] if containers else {}

        # Extract env vars
        env_vars = {}
        for env in container.get('env', []):
            if 'value' in env:
                env_vars[env['name']] = str(env['value'])

        # Check probes
        has_readiness = 'readinessProbe' in container
        has_liveness = 'livenessProbe' in container

        return cls(
            kind=k8s_dict['kind'],
            name=metadata.get('name', 'unknown'),
            namespace=metadata.get('namespace', 'default'),
            raw=k8s_dict,
            replicas=spec.get('replicas', 1),
            env_vars=env_vars,
            annotations=metadata.get('annotations', {}),
            has_readiness_probe=has_readiness,
            has_liveness_probe=has_liveness
        )


@dataclass
class Ingress(KubernetesResource):
    """Kubernetes Ingress"""

    annotations: Dict[str, str]

    @classmethod
    def from_k8s(cls, k8s_dict: Dict):
        """Create Ingress from parsed K8s YAML"""
        metadata = k8s_dict.get('metadata', {})
        return cls(
            kind='Ingress',
            name=metadata.get('name', 'unknown'),
            namespace=metadata.get('namespace', 'default'),
            raw=k8s_dict,
            annotations=metadata.get('annotations', {})
        )
