READ_ROLES = {"owner", "editor", "viewer"}
WRITE_ROLES = {"owner", "editor"}
ACTION_ROLES = {"owner", "editor"}


def can_use_tool(role: str, permission: str) -> bool:
	allowed_roles = {
		"read": READ_ROLES,
		"write": WRITE_ROLES,
		"action": ACTION_ROLES,
	}.get(permission)
	if allowed_roles is None:
		raise ValueError(f"Unknown tool permission: {permission}")
	return role in allowed_roles
