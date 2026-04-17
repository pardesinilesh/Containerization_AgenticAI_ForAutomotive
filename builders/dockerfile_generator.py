"""
Dynamic Dockerfile generator using generic templates and YAML configuration.
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from jinja2 import Template, Environment, FileSystemLoader


class DockerfileGenerator:
    """Generates Dockerfiles from generic templates using YAML tool configuration."""

    def __init__(self, templates_dir: str = "builders/templates", config_dir: str = "config/tools"):
        """
        Initialize generator.

        Args:
            templates_dir: Directory containing Dockerfile templates
            config_dir: Directory containing tool configuration YAML files
        """
        self.templates_dir = templates_dir
        self.config_dir = config_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir)
            if os.path.exists(templates_dir)
            else None
        )

    def _load_tool_config(self, tool: str) -> Dict[str, Any]:
        """
        Load tool configuration from YAML file.

        Args:
            tool: Tool name (e.g., 'trace32', 'canoe')

        Returns:
            Tool configuration dictionary
        """
        config_file = Path(self.config_dir) / f"{tool}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Tool config not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def generate(
        self,
        tool: str,
        os: str,
        version: str,
        plan: Optional[Dict[str, Any]] = None,
        optimization: bool = True,
    ) -> str:
        """
        Generate Dockerfile content using generic template and tool configuration.

        Args:
            tool: Tool name (e.g., 'trace32', 'canoe')
            os: Target OS ('windows' or 'linux')
            version: Tool version
            plan: Build plan from LLM (optional)
            optimization: Apply optimization hints

        Returns:
            Dockerfile content as string
        """
        plan = plan or {}

        # Load tool configuration from YAML
        tool_config = self._load_tool_config(tool)

        # Use generic template based on OS
        if self.env:
            if os.lower() == "windows":
                template_name = "generic_windows.dockerfile.j2"
            else:
                template_name = "generic_linux.dockerfile.j2"
            
            try:
                template = self.env.get_template(template_name)
                dockerfile = template.render(
                    tool=tool,
                    tool_config=tool_config,
                    version=version,
                    **plan
                )
                return dockerfile
            except Exception as e:
                print(f"Error rendering template: {e}")
                # Fall back to generic generation
                pass

        # Fall back to generic generation if template loading fails
        return self._generate_generic_dockerfile(
            tool=tool,
            os=os,
            version=version,
            tool_config=tool_config,
            plan=plan,
        )

    def _generate_generic_dockerfile(
        self,
        tool: str,
        os: str,
        version: str,
        tool_config: Dict[str, Any],
        plan: Dict[str, Any],
    ) -> str:
        """
        Generate a generic Dockerfile when template rendering fails.

        Args:
            tool: Tool name
            os: Target OS
            version: Tool version
            tool_config: Tool configuration dictionary
            plan: Build plan

        Returns:
            Generated Dockerfile content
        """
        base_image = plan.get("base_image", self._get_default_base_image(os))
        docker_config = tool_config.get("docker", {})
        dependencies = tool_config.get("dependencies", {}).get(os.lower(), [])
        env_vars = tool_config.get("environment_variables", {})
        ports = docker_config.get("ports", [])
        volumes = docker_config.get("volumes", [])
        python_deps = tool_config.get("python_dependencies", [])

        dockerfile_lines = [
            f"FROM {base_image}",
            "",
            f"# {tool_config.get('display_name', tool)} - {tool_config.get('description', '')}",
            f"# Version: {version}",
            "",
            f"LABEL tool='{tool}'",
            f"LABEL vendor='{tool_config.get('vendor', 'unknown')}'",
            f"LABEL version='{version}'",
            "",
            "# Install dependencies",
        ]

        if os.lower() == "windows":
            dockerfile_lines.extend([
                "RUN powershell -Command \\",
                "    $ErrorActionPreference = 'Stop'; \\",
                "    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor 3072; \\",
                "    iex ((New-Object Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')); \\",
            ])

            if dependencies:
                for dep in dependencies:
                    dockerfile_lines.append(f"    choco install -y {dep}; \\")
                dockerfile_lines[-1] = dockerfile_lines[-1].rstrip(" \\")
        else:
            dockerfile_lines.add("ENV DEBIAN_FRONTEND=noninteractive")
            dockerfile_lines.append("")
            if dependencies:
                dockerfile_lines.append("RUN apt-get update && apt-get install -y \\")
                for dep in dependencies:
                    dockerfile_lines.append(f"    {dep} \\")
                dockerfile_lines[-1] = dockerfile_lines[-1].rstrip(" \\")
                dockerfile_lines.append("    && rm -rf /var/lib/apt/lists/*")

        # Create working directory
        dockerfile_lines.extend([
            "",
            f"WORKDIR /app/{tool}",
            f"RUN mkdir -p /app/{tool}/{{config,data,logs,projects}}",
        ])

        # Environment variables
        if env_vars:
            dockerfile_lines.append("")
            for key, value in env_vars.items():
                dockerfile_lines.append(f"ENV {key}={value}")

        # Python dependencies
        if python_deps and os.lower() != "windows":
            dockerfile_lines.append("")
            dockerfile_lines.append("RUN pip3 install --no-cache-dir \\")
            for dep in python_deps:
                dockerfile_lines.append(f"    {dep} \\")
            dockerfile_lines[-1] = dockerfile_lines[-1].rstrip(" \\")

        # Expose ports
        if ports:
            dockerfile_lines.append("")
            dockerfile_lines.append(f"EXPOSE {' '.join(map(str, ports))}")

        # Default command
        dockerfile_lines.extend([
            "",
            f"CMD [\"/bin/bash\", \"-c\", \"echo '{tool} {version} container started'\"]",
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
