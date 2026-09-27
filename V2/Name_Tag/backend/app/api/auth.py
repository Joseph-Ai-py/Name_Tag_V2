from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.session import (
    clear_session_cookie,
    create_session,
    get_session_by_token,
    revoke_session,
    set_session_cookie,
)
from app.config import get_settings
from app.core.security import hash_session_token
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    AuthUserResponse,
    LoginRequest,
    SignupRequest,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    payload: SignupRequest,
    response: Response,
    db: Session = Depends(get_database),
):
    existing_user = get_user_by_email(
        db,
        payload.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = create_user(
        db,
        payload.email,
        payload.password,
    )

    token = create_session(db, user)

    set_session_cookie(
        response,
        token,
    )

    return AuthResponse(
        user=AuthUserResponse(
            id=user.id,
            email=user.email,
        )
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_database),
):
    user = authenticate_user(
        db,
        payload.email,
        payload.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_session(db, user)

    set_session_cookie(
        response,
        token,
    )

    return AuthResponse(
        user=AuthUserResponse(
            id=user.id,
            email=user.email,
        )
    )


@router.get(
    "/me",
    response_model=AuthResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return AuthResponse(
        user=AuthUserResponse(
            id=current_user.id,
            email=current_user.email,
        )
    )


@router.post("/logout")
def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_database),
):
    settings = get_settings()

    token = request.cookies.get(
        settings.session_cookie_name
    )

    if token:
        user_session = get_session_by_token(
            db,
            token,
        )

        if user_session is not None:
            revoke_session(
                db,
                user_session,
            )

    clear_session_cookie(response)

    return {
        "status": "ok",
    }
