from typing import Any


def build_context(
	state: dict[str, Any] | None,
	*,
	version: int | None = None,
	conversation_history: list[dict[str, Any]] | None = None,
	user_role: str | None = None,
	goal: str | None = None,
	initial_route: str | None = None,
	pending_proposals: list[dict[str, Any]] | None = None,
	active_research: list[dict[str, Any]] | None = None,
	recent_findings: list[dict[str, Any]] | None = None,
	recent_artifacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
	brand_state = state or {}
	return {
		"brand_state": {
			"version": version,
			"business": brand_state.get("business", {}),
			"market": brand_state.get("market", {}),
			"customer": brand_state.get("customer", {}),
			"brand": brand_state.get("brand", {}),
			"visual": brand_state.get("visual", {}),
		},
		"conversation": {"recent_messages": conversation_history or []},
		"user": {"role": user_role} if user_role else {},
		"goal": goal,
		"pending_proposals": pending_proposals or [],
		"research": {
			"active_jobs": active_research or [],
			"recent_findings": recent_findings or [],
		},
		"recent_artifacts": recent_artifacts or [],
		"agent": {
			"initial_route": initial_route,
			"completed_steps": [],
			"tool_results": {},
			"observed": {},
		},
	}
