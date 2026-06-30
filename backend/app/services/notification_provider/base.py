from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class NotificationProviderReadiness:
    provider: str
    status: str
    mode: str
    external_calls_enabled: bool
    message: str


@dataclass(frozen=True)
class NotificationProviderPayload:
    title: str
    message: str
    channel: str


@dataclass(frozen=True)
class NotificationProviderSendResult:
    provider: str
    channel: str
    delivered: bool
    skipped: bool
    external_calls_enabled: bool
    message: str


class NotificationProviderAdapter(Protocol):
    provider_name: str

    def validate_connection(self) -> NotificationProviderReadiness:
        """Return readiness without using or exposing external notification secrets."""

    def send_message(self, payload: NotificationProviderPayload) -> NotificationProviderSendResult:
        """Send or skip a message. Demo providers must not call external APIs."""
