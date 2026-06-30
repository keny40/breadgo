from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class DeliveryProviderReadiness:
    provider: str
    status: str
    mode: str
    external_calls_enabled: bool
    message: str


@dataclass(frozen=True)
class DeliveryQuoteRequest:
    fulfillment_method: str
    origin_region: str
    destination_region: str
    package_note: str | None = None


@dataclass(frozen=True)
class DeliveryQuoteResult:
    provider: str
    fulfillment_method: str
    delivery_fee: Decimal
    external_calls_enabled: bool
    message: str


@dataclass(frozen=True)
class DeliveryCreateResult:
    provider: str
    delivery_status: str
    external_delivery_id: str | None
    external_calls_enabled: bool
    message: str


class DeliveryProviderAdapter(Protocol):
    provider_name: str

    def validate_connection(self) -> DeliveryProviderReadiness:
        """Return provider readiness without using or exposing external secrets."""

    def quote_delivery(self, request: DeliveryQuoteRequest) -> DeliveryQuoteResult:
        """Return a delivery quote. Demo providers must not call external APIs."""

    def create_delivery(self, request: DeliveryQuoteRequest) -> DeliveryCreateResult:
        """Create a delivery request. Demo providers must not call external APIs."""

    def cancel_delivery(self, external_delivery_id: str) -> DeliveryCreateResult:
        """Cancel a delivery request. Demo providers must not call external APIs."""
