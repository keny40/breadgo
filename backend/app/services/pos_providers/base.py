from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class NormalizedPosItem:
    external_sku: str
    name: str
    description: str | None
    original_price: Decimal
    discount_price: Decimal
    stock_quantity: int
    sale_starts_at: datetime
    sale_ends_at: datetime
    pickup_available: bool
    quick_delivery_available: bool
    parcel_delivery_available: bool
    quick_delivery_fee: Decimal
    parcel_delivery_fee: Decimal


class PosProviderAdapter(Protocol):
    provider_name: str

    def validate_connection(self) -> tuple[bool, str | None]:
        """Return connection readiness without exposing sensitive provider details."""

    def fetch_items(self) -> list[object]:
        """Fetch raw provider items. Real providers will implement this later."""

    def normalize_item(self, item: object) -> NormalizedPosItem:
        """Convert provider-specific item shape to BreadGo's normalized POS item."""
