"""
Dynamic Dockerfile generator using templates and LLM intelligence.
"""
import os
from typing import Optional, Dict, Any, List
from jinja2 import Template, Environment, FileSystemLoader


class DockerfileGenerator:
    """Generates Dockerfiles from templates using LLM-guided optimization."""

    def __init__(self, templates_dir: str = "builders/templates"):
        """
        Initialize generator.

        Args:
            templates_dir: Directory containing Dockerfile templates
        """
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir)
            if os.path.exists(templates_dir)
            else None
        )

    def generate(
        self,
        tool: str,
        os: str,
        version: str,
        plan: Optional[Dict[str, Any]] = None,
        optimization: bool = True,
    ) -> str:
        """
        Generate Dockerfile content.

        Args:
            tool: Tool name (e.g., 'trace32')
            os: Target OS ('windows' or 'linux')
            version: Tool version
            plan: Build plan from LLM
            optimization: Apply optimization hints

        Returns:
            Dockerfile content as string
        """
        plan = plan or {}

        # Load base template or generate from scratch
        if self.env:
            template_name = f"{tool}_{os}.dockerfile"
            try:
                template = self.env.get_template(template_name)
                dockerfile = template.render(
                    tool=tool,
                    version=version,
                    **plan
                )
                return dockerfile
            except Exception:
                pass

        # Fall back to generic generation
        return self._generate_generic_dockerfile(
            tool=tool,
            os=os,
            version=version,
            plan=plan,
        )

    def _generate_generic_dockerfile(
        self,
        tool: str,
        os: str,
        version: str,
        plan: Dict[str, Any],
    ) -> str:
        """
        Generate a generic Dockerfile when no template exists.

        Args:
            tool: Tool name
            os: Target OS
            version: Tool version
            plan: Build plan

        Returns:
            Generated Dockerfile content
        """
        base_image = plan.get("base_image", self._get_default_base_image(os))
        dependencies = plan.get("dependencies", [])
        env_vars = plan.get("env_variables", {})
        ports = plan.get("ports", [])
        volumes = plan.get("volumes", [])

        dockerfile_lines = [
            f"FROM {base_image}",
            "",
            f"# Automotive Development Tool: {tool}",
            f"# Version: {version}",
            f"# OS: {os}",
            "",
            "LABEL maintainer='automotive-team@local'",
            f"LABEL tool='{tool}'",
            f"LABEL version='{version}'",
            "",
            "# Install dependencies",
        ]

        if os.lower() == "windows":
            dockerfile_lines.extend([
                "RUN powershell -Command \\",
                "    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process; \\",
                "    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12",
            ])

            if dependencies:
                dockerfile_lines.append("    && choco install -y \\")
                for dep in dependencies:
                    dockerfile_lines.append(f"        {dep} \\")
                dockerfile_lines[-1] = dockerfile_lines[-1].rstrip(" \\")
        else:
            if dependencies:
                dockerfile_lines.extend([
                    "RUN apt-get update && apt-get install -y \\",
                ])
                for dep in dependencies:
                    dockerfile_lines.append(f"    {dep} \\")
                dockerfile_lines[-1] = dockerfile_lines[-1].rstrip(" \\")
                dockerfile_lines.append("    && rm -rf /var/lib/apt/lists/*")

        # Environment variables
        if env_vars:
            dockerfile_lines.append("")
            dockerfile_lines.append("# Environment variables")
            for key, value in env_vars.items():
                dockerfile_lines.append(f"ENV {key}={value}")

        # Create working directory
        dockerfile_lines.extend([
            "",
            f"WORKDIR /app/{tool}",
            f"RUN mkdir -p /app/{tool}/data",
        ])

        # Expose ports
        if ports:
            dockerfile_lines.append("")
            for port in ports:
                dockerfile_lines.append(f"EXPOSE {port}")

        # Volumes
        if volumes:
            dockerfile_lines.append("")
            for volume in volumes:
                dockerfile_lines.append(f"VOLUME {volume}")

        # Default command
        dockerfile_lines.extend([
            "",
            "# Health check",
            "HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\",
            f"    CMD echo '{tool} container is running'",
            "",
            f"CMD [\"/bin/bash\", \"-c\", \"echo '{tool} {version} ready'\"]",
        ])

        return "\n".join(dockerfile_lines)

    def _get_default_base_image(self, os: str) -> str:
        """Get default base image for OS."""
        if os.lower() == "windows":
            return "mcr.microsoft.com/windows/servercore:ltsc2022"
        else:
            return "ubuntu:22.04"

    def validate_dockerfile(self, dockerfile_content: str) -> tuple[bool, List[str]]:
        """
        Validate Dockerfile syntax.

        Args:
            dockerfile_content: Dockerfile content to validate

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        lines = dockerfile_content.split("\n")

        required_commands = {"FROM", "WORKDIR", "CMD"}
        found_commands = set()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Check for required commands
            for cmd in required_commands:
                if stripped.startswith(cmd):
                    found_commands.add(cmd)

            # Basic syntax validation
            if stripped.startswith("RUN ") and not stripped.endswith("\\"):
                if i < len(lines) and not lines[i].startswith("    "):
                    pass  # OK for single line RUN

        for cmd in required_commands:
            if cmd not in found_commands:
                errors.append(f"Missing required command: {cmd}")

        return len(errors) == 0, errors
