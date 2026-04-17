"""
Config package initialization.
"""
import os
import yaml
from pathlib import Path


def load_config(env: str = "dev") -> dict:
    """
    Load environment configuration.

    Args:
        env: Environment name

    Returns:
        Configuration dictionary
    """
    config_path = Path(__file__).parent / "environments" / f"{env}.yaml"

    if not config_path.exists():
        return {}

    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def load_tool_config(tool: str) -> dict:
    """
    Load tool-specific configuration.

    Args:
        tool: Tool name

    Returns:
        Tool configuration dictionary
    """
    config_path = Path(__file__).parent / "tools" / f"{tool}.yaml"

    if not config_path.exists():
        return {}

    with open(config_path) as f:
        return yaml.safe_load(f) or {}
