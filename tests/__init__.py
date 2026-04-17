"""
Tests initialization package.
"""
import pytest


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "tool": "trace32",
        "os": "linux",
        "version": "test",
    }
