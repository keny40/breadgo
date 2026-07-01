from uuid import UUID

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from app.core.config import settings
from app.schemas.auth import GoogleOAuthStatusResponse, TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.google_oauth_service import (
    authenticate_google_customer,
    build_google_authorization_url,
    fetch_google_profile_from_code,
    google_oauth_configured,
)


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        parsed_user_id = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token subject.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.get(User, parsed_user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not available.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing_user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.")

    if payload.phone:
        existing_phone = db.scalar(select(User).where(User.phone == payload.phone))
        if existing_phone is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone is already registered.")

    user = User(
        email=payload.email.lower(),
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name.strip(),
        role=payload.role,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the supplied email or phone already exists.",
        ) from exc

    db.refresh(user)
    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")

    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/google/status", response_model=GoogleOAuthStatusResponse)
def google_oauth_status() -> GoogleOAuthStatusResponse:
    enabled = google_oauth_configured()
    message = (
        "Google OAuth is enabled for customer accounts."
        if enabled
        else "Google OAuth is disabled or not configured for this environment."
    )
    return GoogleOAuthStatusResponse(enabled=enabled, message=message)


@router.get("/google/start")
def google_oauth_start() -> RedirectResponse:
    return RedirectResponse(build_google_authorization_url(), status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
def google_oauth_callback(
    code: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    callback_url = f"{settings.FRONTEND_URL.rstrip('/')}/auth/google/callback"

    if error:
        query = urlencode({"error": "Google login was cancelled or denied."})
        return RedirectResponse(f"{callback_url}?{query}", status_code=status.HTTP_302_FOUND)

    if not code:
        query = urlencode({"error": "Google OAuth callback did not include an authorization code."})
        return RedirectResponse(f"{callback_url}?{query}", status_code=status.HTTP_302_FOUND)

    try:
        profile = fetch_google_profile_from_code(code)
        token_response = authenticate_google_customer(db, profile)
    except HTTPException as exc:
        query = urlencode({"error": str(exc.detail)})
        return RedirectResponse(f"{callback_url}?{query}", status_code=status.HTTP_302_FOUND)

    query = urlencode({"token": token_response.access_token})
    return RedirectResponse(f"{callback_url}?{query}", status_code=status.HTTP_302_FOUND)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
