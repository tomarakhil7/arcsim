"""Request flow graph builder"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import networkx as nx

from ..models.resource import Ingress, Deployment
from ..models.timeout import Timeout
from ..parsers.timeout_extractor import TimeoutExtractor


@dataclass
class FlowNode:
    """Node in request flow graph"""

    name: str
    type: str  # "ingress", "service", "database"
    timeout: Optional[Timeout]
    resource: Any


class RequestFlowGraph:
    """Build request flow graph from K8s resources"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, FlowNode] = {}
        self.timeout_extractor = TimeoutExtractor()

    def add_ingress(self, ingress: Ingress):
        """Add ingress to graph

        Args:
            ingress: Ingress resource
        """
        timeouts = self.timeout_extractor.extract_from_nginx_ingress(ingress)

        # Use the read timeout if available (most relevant for request flow)
        timeout = next((t for t in timeouts if 'read' in t.resource_name), None)
        if not timeout and timeouts:
            # Fall back to first timeout
            timeout = timeouts[0]

        node = FlowNode(
            name=f"ingress:{ingress.name}",
            type="ingress",
            timeout=timeout,
            resource=ingress
        )

        self.nodes[node.name] = node
        self.graph.add_node(node.name, data=node)

    def add_deployment(self, deployment: Deployment):
        """Add deployment to graph

        Args:
            deployment: Deployment resource
        """
        # Extract timeouts
        timeouts = self.timeout_extractor.extract_from_deployment(deployment)
        db_timeouts = self.timeout_extractor.extract_from_deployment_db_refs(deployment)

        # Service timeout (first HTTP timeout found)
        service_timeout = next(iter(timeouts), None) if timeouts else None

        node = FlowNode(
            name=f"service:{deployment.name}",
            type="service",
            timeout=service_timeout,
            resource=deployment
        )

        self.nodes[node.name] = node
        self.graph.add_node(node.name, data=node)

        # If there's a DB connection, add DB node
        if db_timeouts:
            db_node = FlowNode(
                name=f"database:{deployment.name}-db",
                type="database",
                timeout=db_timeouts[0],
                resource=None
            )
            self.nodes[db_node.name] = db_node
            self.graph.add_node(db_node.name, data=db_node)

            # Add edge: service -> database
            self.graph.add_edge(node.name, db_node.name)

    def infer_connections(self, ingresses: List[Ingress], deployments: List[Deployment]):
        """Infer connections between ingress and services

        Uses simple heuristic: match by name

        Args:
            ingresses: List of Ingress resources
            deployments: List of Deployment resources
        """

        # Simple heuristic: match by name
        for ingress in ingresses:
            for deployment in deployments:
                # If ingress name contains deployment name or vice versa, connect them
                ingress_name_lower = ingress.name.lower()
                deployment_name_lower = deployment.name.lower()

                # Remove common suffixes/prefixes for better matching
                for common in ['-ingress', '-ing', '-service', '-svc', '-api']:
                    ingress_name_lower = ingress_name_lower.replace(common, '')
                    deployment_name_lower = deployment_name_lower.replace(common, '')

                if (deployment_name_lower in ingress_name_lower or
                    ingress_name_lower in deployment_name_lower or
                    ingress_name_lower == deployment_name_lower):

                    ingress_node = f"ingress:{ingress.name}"
                    service_node = f"service:{deployment.name}"

                    if ingress_node in self.graph and service_node in self.graph:
                        self.graph.add_edge(ingress_node, service_node)

    def get_request_paths(self) -> List[List[FlowNode]]:
        """Get all request paths through the system

        Returns:
            List of paths, where each path is a list of FlowNode objects
        """
        paths = []

        # Find all ingress nodes (entry points)
        ingress_nodes = [n for n in self.graph.nodes() if n.startswith('ingress:')]

        # Find all leaf nodes (endpoints)
        leaf_nodes = [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]

        # Find paths from each ingress to each leaf
        for ingress in ingress_nodes:
            for leaf in leaf_nodes:
                try:
                    for path in nx.all_simple_paths(self.graph, ingress, leaf):
                        # Convert to FlowNode objects
                        path_nodes = [self.nodes[n] for n in path]
                        paths.append(path_nodes)
                except nx.NetworkXNoPath:
                    continue

        return paths
