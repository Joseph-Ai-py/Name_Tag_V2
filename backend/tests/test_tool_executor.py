import pytest

from app.models.user import User
from app.tools.base import ToolContext
from app.tools.executor import ToolExecutor
from app.tools.registry import tool_registry
from conftest import signup
from test_brands_and_state import create_brand


def test_tool_executor_reads_context_and_creates_document(client) -> None:
    signup(client, "tools@example.com")
    brand_id = create_brand(client)
    user_id = client.get("/api/auth/me").json()["user"]["id"]

    from app.dependencies import get_database

    db_generator = client.app.dependency_overrides[get_database]()
    db = next(db_generator)
    try:
        context = ToolContext(db=db, user_id=user_id, brand_id=brand_id, role="owner")
        executor = ToolExecutor()
        state = executor.execute("get_brand_state", context)
        document = executor.execute("create_document", context, title="Tool Document")
        assert state["version"] == 1
        assert document.title == "Tool Document"
    finally:
        db.close()


def test_tool_executor_enforces_role_permission(client) -> None:
    signup(client, "viewer@example.com")
    brand_id = create_brand(client)
    user_id = client.get("/api/auth/me").json()["user"]["id"]
    from app.dependencies import get_database

    db_generator = client.app.dependency_overrides[get_database]()
    db = next(db_generator)
    try:
        context = ToolContext(db=db, user_id=user_id, brand_id=brand_id, role="viewer")
        with pytest.raises(PermissionError):
            ToolExecutor().execute("create_document", context, title="Blocked")
    finally:
        db.close()