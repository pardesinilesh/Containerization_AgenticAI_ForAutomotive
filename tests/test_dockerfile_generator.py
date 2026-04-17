"""
Tests for Dockerfile generation.
"""
import pytest
from builders.dockerfile_generator import DockerfileGenerator


@pytest.fixture
def generator():
    """Provide dockerfile generator."""
    return DockerfileGenerator()


def test_generate_linux_dockerfile(generator):
    """Test Linux Dockerfile generation."""
    dockerfile = generator.generate(
        tool="trace32",
        os="linux",
        version="1.0.0",
    )
    assert "FROM ubuntu" in dockerfile
    assert "EXPOSE 2000" in dockerfile


def test_generate_windows_dockerfile(generator):
    """Test Windows Dockerfile generation."""
    dockerfile = generator.generate(
        tool="trace32",
        os="windows",
        version="1.0.0",
    )
    assert "FROM mcr.microsoft.com/windows" in dockerfile


def test_dockerfile_validation(generator):
    """Test Dockerfile validation."""
    valid_dockerfile = """
FROM ubuntu:22.04
WORKDIR /app
CMD ["/bin/bash"]
"""
    is_valid, errors = generator.validate_dockerfile(valid_dockerfile)
    assert is_valid is True
    assert len(errors) == 0


def test_dockerfile_validation_missing_from(generator):
    """Test validation catches missing FROM."""
    invalid_dockerfile = """
WORKDIR /app
CMD ["/bin/bash"]
"""
    is_valid, errors = generator.validate_dockerfile(invalid_dockerfile)
    assert is_valid is False
    assert any("FROM" in error for error in errors)
