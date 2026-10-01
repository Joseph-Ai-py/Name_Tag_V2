import pytest

from app.agent.permissions import can_use_tool
from app.tools.registry import ToolRegistry, tool_registry


def test_tool_registry_has_permission_categories() -> None:
    assert tool_registry.get("get_brand_state").permission == "read"
    assert tool_registry.get("apply_brand_change").permission == "action"
    assert "create_document" in tool_registry.names()


def test_tool_permissions_follow_brand_roles() -> None:
    assert can_use_tool("viewer", "read")
    assert not can_use_tool("viewer", "write")
    assert can_use_tool("editor", "action")
    assert can_use_tool("owner", "write")


def test_registry_rejects_duplicates_and_unknown_tools() -> None:
    registry = ToolRegistry()
    registry.register(tool_registry.get("get_brand_state"))
    with pytest.raises(ValueError, match="already registered"):
        registry.register(tool_registry.get("get_brand_state"))
    with pytest.raises(ValueError, match="Unknown tool"):
        registry.get("missing")