#!/usr/bin/env python3
"""
Setup script for Heavy Bag Training game.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="heavy-bag-training",
    version="1.0.0",
    author="Heavy Bag Training Team",
    description="A professional boxing training game with realistic physics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/heavy-bag-training",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment :: Simulation",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "heavy-bag-training=src.main:main",
        ],
    },
    package_data={
        "src": ["assets/*", "assets/**/*"],
    },
    include_package_data=True,
)
