from app.schemas.pos_integration import MockPosItem
from app.services.pos_providers.base import NormalizedPosItem


class MockPosProvider:
    provider_name = "MOCK_POS"

    def __init__(self, mock_items: list[MockPosItem]) -> None:
        self._mock_items = mock_items

    def validate_connection(self) -> tuple[bool, str | None]:
        return True, None

    def fetch_items(self) -> list[MockPosItem]:
        return self._mock_items

    def normalize_item(self, item: object) -> NormalizedPosItem:
        if not isinstance(item, MockPosItem):
            raise ValueError("INVALID_MOCK_POS_ITEM")
        return NormalizedPosItem(
            external_sku=item.external_sku.strip(),
            name=item.name.strip(),
            description=item.description.strip() if item.description else None,
            original_price=item.original_price,
            discount_price=item.discount_price,
            stock_quantity=item.stock_quantity,
            sale_starts_at=item.sale_starts_at,
            sale_ends_at=item.sale_ends_at,
            pickup_available=item.pickup_available,
            quick_delivery_available=item.quick_delivery_available,
            parcel_delivery_available=item.parcel_delivery_available,
            quick_delivery_fee=item.quick_delivery_fee,
            parcel_delivery_fee=item.parcel_delivery_fee,
        )
