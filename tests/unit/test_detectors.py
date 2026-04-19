"""Test detector functionality"""

import pytest
from arcsim.detectors.spof import SPOFDetector
from arcsim.detectors.health_probes import HealthProbeDetector
from arcsim.models.resource import Deployment


def test_spof_detector_production():
    """SPOF should be detected in production with 1 replica"""
    detector = SPOFDetector()

    deployment = Deployment(
        kind='Deployment',
        name='test-service',
        namespace='production',
        raw={},
        replicas=1,
        env_vars={},
        annotations={},
        has_readiness_probe=True,
        has_liveness_probe=True
    )

    findings = detector.check(deployment, 'production')

    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"
    assert "SPOF" in findings[0].title


def test_spof_detector_no_issue_multiple_replicas():
    """No SPOF with multiple replicas"""
    detector = SPOFDetector()

    deployment = Deployment(
        kind='Deployment',
        name='test-service',
        namespace='production',
        raw={},
        replicas=3,
        env_vars={},
        annotations={},
        has_readiness_probe=True,
        has_liveness_probe=True
    )

    findings = detector.check(deployment, 'production')
    assert len(findings) == 0


def test_spof_detector_ignored_in_staging():
    """SPOF should be ignored in non-production"""
    detector = SPOFDetector()

    deployment = Deployment(
        kind='Deployment',
        name='test-service',
        namespace='staging',
        raw={},
        replicas=1,
        env_vars={},
        annotations={},
        has_readiness_probe=True,
        has_liveness_probe=True
    )

    findings = detector.check(deployment, 'staging')
    assert len(findings) == 0


def test_health_probe_detector_missing_readiness():
    """Missing readiness probe should be detected"""
    detector = HealthProbeDetector()

    deployment = Deployment(
        kind='Deployment',
        name='test-service',
        namespace='production',
        raw={},
        replicas=3,
        env_vars={},
        annotations={},
        has_readiness_probe=False,
        has_liveness_probe=True
    )

    findings = detector.check(deployment, 'production')

    # Should find missing readiness probe
    assert len(findings) >= 1
    readiness_findings = [f for f in findings if 'Readiness' in f.title]
    assert len(readiness_findings) == 1
    assert readiness_findings[0].severity == "CRITICAL"


def test_health_probe_detector_all_present():
    """No issues when all probes present"""
    detector = HealthProbeDetector()

    deployment = Deployment(
        kind='Deployment',
        name='test-service',
        namespace='production',
        raw={},
        replicas=3,
        env_vars={},
        annotations={},
        has_readiness_probe=True,
        has_liveness_probe=True
    )

    findings = detector.check(deployment, 'production')
    assert len(findings) == 0
