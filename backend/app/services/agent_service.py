from sqlalchemy.orm import Session

from app.agent.core import AgentCore
from app.agent.state import AgentBudget
from app.models.user import User
from app.services.brand_service import get_brand_membership
from app.skills.executor import SkillExecutor
from app.tools.executor import ToolExecutor


DEFAULT_BUDGET = AgentBudget(max_iterations=8, max_tool_calls=8, max_llm_calls=8)


def _select_skill(route: str, message: str) -> str:
    """Compatibility wrapper for callers that still inspect the legacy helper."""
    return AgentCore._select_skill(route, message)


def run_agent(
    db: Session,
    current_user: User,
    brand_id: str,
    conversation_id: str | None,
    message: str,
) -> dict:
    membership = get_brand_membership(db, brand_id, current_user.id)
    if membership is None:
        raise ValueError("Brand not found")

    core = AgentCore(
        db=db,
        user=current_user,
        brand_id=brand_id,
        role=membership.role,
        tool_executor=ToolExecutor(),
        skill_executor=SkillExecutor(),
        budget=DEFAULT_BUDGET,
    )
    return core.run(conversation_id=conversation_id, message=message)
