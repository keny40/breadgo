from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.user import User, UserRole
from app.services.google_oauth_service import GoogleOAuthProfile, authenticate_google_customer


class FakeDb:
    def __init__(self, existing_user: User | None = None) -> None:
        self.existing_user = existing_user
        self.added_user: User | None = None
        self.committed = False

    def scalar(self, _statement: object) -> User | None:
        return self.existing_user

    def add(self, user: User) -> None:
        self.added_user = user

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False

    def refresh(self, user: User) -> None:
        if user.id is None:
            user.id = uuid4()


def _user(email: str, role: UserRole = UserRole.CUSTOMER, is_active: bool = True) -> User:
    return User(
        id=uuid4(),
        email=email,
        phone=None,
        password_hash="hashed-password",
        full_name="OAuth User",
        role=role,
        is_active=is_active,
    )


def _profile(email: str = "google.customer@example.com", verified: bool = True) -> GoogleOAuthProfile:
    return GoogleOAuthProfile(
        email=email,
        email_verified=verified,
        name="Google Customer",
        sub="google-subject-id",
    )


def test_google_oauth_creates_new_customer_without_storing_google_tokens() -> None:
    db = FakeDb()

    response = authenticate_google_customer(db, _profile())

    assert response.access_token
    assert response.user.email == "google.customer@example.com"
    assert response.user.role == UserRole.CUSTOMER
    assert db.added_user is not None
    assert db.added_user.role == UserRole.CUSTOMER
    assert db.added_user.phone is None
    assert db.committed is True
    assert not hasattr(db.added_user, "google_access_token")
    assert not hasattr(db.added_user, "google_refresh_token")


def test_google_oauth_logs_in_existing_customer() -> None:
    existing = _user("existing.customer@example.com", UserRole.CUSTOMER)
    db = FakeDb(existing)

    response = authenticate_google_customer(db, _profile("existing.customer@example.com"))

    assert response.access_token
    assert response.user.email == existing.email
    assert response.user.role == UserRole.CUSTOMER
    assert db.added_user is None
    assert db.committed is False


def test_google_oauth_rejects_unverified_email() -> None:
    db = FakeDb()

    with pytest.raises(HTTPException) as exc:
        authenticate_google_customer(db, _profile(verified=False))

    assert exc.value.status_code == 403
    assert "not verified" in str(exc.value.detail)
    assert db.added_user is None


@pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.MERCHANT])
def test_google_oauth_rejects_existing_non_customer_accounts(role: UserRole) -> None:
    db = FakeDb(_user(f"{role.value}@example.com", role))

    with pytest.raises(HTTPException) as exc:
        authenticate_google_customer(db, _profile(f"{role.value}@example.com"))

    assert exc.value.status_code == 403
    assert "customer accounts only" in str(exc.value.detail)
    assert db.added_user is None
