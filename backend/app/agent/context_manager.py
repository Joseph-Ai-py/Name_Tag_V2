from typing import Any


def build_context(state: dict[str, Any] | None) -> dict[str, Any]:
	if not state:
		return {}

	return {
		"business": state.get("business", {}),
		"market": state.get("market", {}),
		"customer": state.get("customer", {}),
		"brand": state.get("brand", {}),
		"visual": state.get("visual", {}),
	}
