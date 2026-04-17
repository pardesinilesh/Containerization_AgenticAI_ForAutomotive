"""
Utilities for configuration loading and management.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any


def load_env_config(env: str = None) -> Dict[str, Any]:
    """
    Load environment configuration.

    Args:
        env: Environment name (default from ENV variable)

    Returns:
        Configuration dictionary
    """
    env = env or os.getenv("ENVIRONMENT", "dev")
    config_dir = Path(__file__).parent / "config" / "environments"
    config_file = config_dir / f"{env}.yaml"

    if not config_file.exists():
        raise FileNotFoundError(f"Config not found: {config_file}")

    with open(config_file) as f:
        return yaml.safe_load(f) or {}


def get_database_url() -> str:
    """Get database URL from config or environment."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/automotive"
    )


def get_registry_url() -> str:
    """Get container registry URL."""
    return os.getenv("REGISTRY_URL", "localhost:5000")
