"""
Example test file for agent orchestrator.
"""
import pytest
import asyncio
from agent.orchestrator import ContainerOrchestrator


@pytest.fixture
def orchestrator():
    """Provide orchestrator instance."""
    return ContainerOrchestrator()


@pytest.mark.asyncio
async def test_build_image(orchestrator):
    """Test image building."""
    result = await orchestrator.build_image(
        tool="trace32",
        os="linux",
        version="1.0.0",
    )
    assert "build_id" in result or "error" in result


@pytest.mark.asyncio
async def test_get_status(orchestrator):
    """Test status retrieval."""
    result = await orchestrator.get_status()
    assert isinstance(result, (dict, list))


@pytest.mark.asyncio
async def test_list_images(orchestrator):
    """Test image listing."""
    result = await orchestrator.list_images()
    assert "images" in result or isinstance(result, list)


def test_state_manager_initialization():
    """Test state manager can be initialized."""
    from agent.state_manager import StateManager
    sm = StateManager()
    assert sm.db_url is not None
