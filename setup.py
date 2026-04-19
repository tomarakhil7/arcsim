"""ArcSim setup"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="arcsim",
    version="0.1.0",
    description="Reliability guardrails for infrastructure",
    author="Your Name",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "arcsim=arcsim.main:main",
        ],
    },
)
