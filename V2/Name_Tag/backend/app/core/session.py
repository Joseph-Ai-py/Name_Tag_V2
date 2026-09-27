from datetime import datetime, timedelta, timezone

from fastapi import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.security import (
    generate_session_token,
    hash_session_token,
)
from app.models.session import Session as UserSession
from app.models.user import User


settings = get_settings()

SESSION_DURATION_DAYS = 7


def create_session(
    db: Session,
    user: User,
) -> str:
    raw_token = generate_session_token()

    user_session = UserSession(
        user_id=user.id,
        token_hash=hash_session_token(raw_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=SESSION_DURATION_DAYS),
    )

    db.add(user_session)
    db.commit()

    return raw_token


def set_session_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=settings.session_cookie_http_only,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_same_site,
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
    )


def get_session_by_token(
    db: Session,
    token: str,
) -> UserSession | None:
    token_hash = hash_session_token(token)

    result = db.execute(
        select(UserSession).where(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
        )
    )

    user_session = result.scalar_one_or_none()

    if user_session is None:
        return None

    now = datetime.now(timezone.utc)

    expires_at = user_session.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        return None

    return user_session


def revoke_session(
    db: Session,
    user_session: UserSession,
) -> None:
    user_session.revoked_at = datetime.now(timezone.utc)
    db.commit()
