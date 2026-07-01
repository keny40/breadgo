from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole


class UserRegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.CUSTOMER

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("email must contain a valid @ address")
        return value


class UserLoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("email must contain a valid @ address")
        return value


class UserResponse(BaseModel):
    id: UUID
    email: str
    phone: str | None
    full_name: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class GoogleOAuthStatusResponse(BaseModel):
    enabled: bool
    message: str
