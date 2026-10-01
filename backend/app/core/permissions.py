from fastapi import HTTPException, status

EDITOR_ROLES = {"owner", "editor"}
OWNER_ROLES = {"owner"}


def require_editor_role(role: str) -> None:
    if role not in EDITOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor permission required",
        )


def require_owner_role(role: str) -> None:
    if role not in OWNER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner permission required",
        )