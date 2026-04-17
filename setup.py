from setuptools import setup, find_packages

setup(
    name="automotive-containerization",
    version="0.1.0",
    description="Agentic AI system for building and deploying scalable containers in Automotive domain",
    author="Automotive Development Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "auto-container=agent.cli:main",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
