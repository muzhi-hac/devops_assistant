"""Setup script for Parallax OpsPilot."""
from setuptools import find_packages, setup

setup(
    name="parallax-ops",
    version="0.1.0",
    description="Terminal-based AI copilot for DevOps engineers",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "pop=src.main:main",
        ],
    },
)

