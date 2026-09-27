from collections.abc import Generator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.session import get_session_by_token
from app.db.session import get_db
from app.models.user import User


def get_database() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    request: Request,
    db: Session = Depends(get_database),
) -> User:
    from app.config import get_settings

    settings = get_settings()

    token = request.cookies.get(
        settings.session_cookie_name
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_session = get_session_by_token(db, token)

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    user = db.get(User, user_session.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
