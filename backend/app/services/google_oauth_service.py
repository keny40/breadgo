from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import secrets

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.schemas.auth import TokenResponse, UserResponse


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_OAUTH_SCOPES = "openid email profile"


@dataclass(frozen=True)
class GoogleOAuthProfile:
    email: str
    email_verified: bool
    name: str | None = None
    sub: str | None = None


def google_oauth_configured() -> bool:
    return bool(
        settings.GOOGLE_OAUTH_ENABLED
        and settings.GOOGLE_CLIENT_ID
        and settings.GOOGLE_CLIENT_SECRET
        and settings.GOOGLE_REDIRECT_URI
    )


def build_google_authorization_url() -> str:
    if not google_oauth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not enabled for this environment.",
        )

    query = urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": GOOGLE_OAUTH_SCOPES,
            "access_type": "online",
            "prompt": "select_account",
            "state": secrets.token_urlsafe(16),
        },
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def fetch_google_profile_from_code(code: str) -> GoogleOAuthProfile:
    if not google_oauth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not enabled for this environment.",
        )

    token_payload = urlencode(
        {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    ).encode("utf-8")
    token_request = Request(
        GOOGLE_TOKEN_URL,
        data=token_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(token_request, timeout=10) as response:
            token_body = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google OAuth token exchange failed.",
        ) from exc

    access_token = token_body.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google OAuth token response did not include an access token.",
        )

    userinfo_request = Request(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urlopen(userinfo_request, timeout=10) as response:
            profile_body = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google profile lookup failed.",
        ) from exc

    return GoogleOAuthProfile(
        email=str(profile_body.get("email") or ""),
        email_verified=bool(profile_body.get("email_verified")),
        name=profile_body.get("name"),
        sub=profile_body.get("sub"),
    )


def authenticate_google_customer(db: Session, profile: GoogleOAuthProfile) -> TokenResponse:
    email = profile.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google profile email is invalid.")

    if not profile.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google email is not verified.",
        )

    user = db.scalar(select(User).where(User.email == email))
    if user is not None:
        if user.role != UserRole.CUSTOMER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Google OAuth is available for customer accounts only.",
            )
        user_status = getattr(user, "status", None) or UserStatus.ACTIVE
        if not user.is_active or user_status != UserStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")
        if getattr(user, "status", None) is None:
            user.status = UserStatus.ACTIVE

        access_token = create_access_token(str(user.id))
        return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))

    display_name = (profile.name or email.split("@")[0]).strip() or "Google Customer"
    user = User(
        email=email,
        phone=None,
        password_hash=get_password_hash(secrets.token_urlsafe(32)),
        full_name=display_name[:255],
        role=UserRole.CUSTOMER,
        is_active=True,
        status=UserStatus.ACTIVE,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.") from exc

    db.refresh(user)
    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))
