"""Main ArcSim engine"""

import sys
import argparse
from pathlib import Path
from typing import List

from .parsers.kubernetes import KubernetesParser
from .parsers.terraform import TerraformParser
from .detectors.spof import SPOFDetector
from .detectors.health_probes import HealthProbeDetector
from .detectors.db_ha import DatabaseHADetector
from .detectors.timeout_chain import TimeoutChainDetector
from .graph.builder import RequestFlowGraph
from .models.finding import Finding
from .reporters.markdown import MarkdownReporter


class ArcSim:
    """Main ArcSim engine"""

    def __init__(self):
        self.k8s_parser = KubernetesParser()
        self.tf_parser = TerraformParser()

        # Initialize detectors
        self.spof_detector = SPOFDetector()
        self.health_probe_detector = HealthProbeDetector()
        self.db_ha_detector = DatabaseHADetector()
        self.timeout_chain_detector = TimeoutChainDetector()

    def analyze_files(self, filepaths: List[str]) -> List[Finding]:
        """Analyze a list of files and return findings

        Args:
            filepaths: List of file paths to analyze

        Returns:
            List of Finding objects
        """
        all_findings = []

        # First pass: collect all resources
        all_k8s_resources = []
        all_tf_resources = []

        for filepath in filepaths:
            path = Path(filepath)

            if not path.exists():
                print(f"Warning: File not found: {filepath}", file=sys.stderr)
                continue

            if path.suffix in ['.yaml', '.yml']:
                try:
                    resources = self.k8s_parser.parse_file(filepath)
                    all_k8s_resources.extend(resources)
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}", file=sys.stderr)

            elif path.suffix == '.tf':
                try:
                    resources = self.tf_parser.parse_file(filepath)
                    all_tf_resources.extend(resources)
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}", file=sys.stderr)

        # Second pass: run simple detectors
        for resource in all_k8s_resources:
            env = self.k8s_parser.get_environment(resource)

            if resource.is_deployment:
                all_findings.extend(self.spof_detector.check(resource, env))
                all_findings.extend(self.health_probe_detector.check(resource, env))

        for resource in all_tf_resources:
            env = self.tf_parser.get_environment_from_tags(resource)
            all_findings.extend(self.db_ha_detector.check(resource, env))

        # Third pass: build graph and run timeout chain analysis
        graph = RequestFlowGraph()

        ingresses = [r for r in all_k8s_resources if r.is_ingress]
        deployments = [r for r in all_k8s_resources if r.is_deployment]

        for ingress in ingresses:
            graph.add_ingress(ingress)

        for deployment in deployments:
            graph.add_deployment(deployment)

        graph.infer_connections(ingresses, deployments)

        # Run timeout chain detection
        timeout_findings = self.timeout_chain_detector.check(graph)
        all_findings.extend(timeout_findings)

        return all_findings


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='ArcSim - Reliability linter for infrastructure',
        epilog='Example: python -m arcsim.main --files changed_files.txt'
    )
    parser.add_argument(
        '--files',
        required=True,
        help='File containing list of paths to analyze (one per line)'
    )
    parser.add_argument(
        '--format',
        default='markdown',
        choices=['markdown', 'json'],
        help='Output format (default: markdown)'
    )

    args = parser.parse_args()

    # Read file list
    try:
        with open(args.files, 'r') as f:
            filepaths = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File list not found: {args.files}", file=sys.stderr)
        sys.exit(1)

    if not filepaths:
        print("No files to analyze", file=sys.stderr)
        sys.exit(0)

    # Run analysis
    arcsim = ArcSim()
    findings = arcsim.analyze_files(filepaths)

    # Generate report
    if args.format == 'markdown':
        reporter = MarkdownReporter()
        report = reporter.generate(findings)
        print(report)
    elif args.format == 'json':
        import json
        findings_dict = [
            {
                'severity': f.severity,
                'rule_id': f.rule_id,
                'title': f.title,
                'message': f.message,
                'resource_name': f.resource_name,
                'resource_kind': f.resource_kind,
                'confidence': f.confidence
            }
            for f in findings
        ]
        print(json.dumps(findings_dict, indent=2))


if __name__ == '__main__':
    main()
