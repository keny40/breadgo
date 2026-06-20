from app.services.pos_providers.base import NormalizedPosItem


class GenericPosProvider:
    provider_name = "GENERIC_POS"

    def validate_connection(self) -> tuple[bool, str | None]:
        return False, "GENERIC_POS_PROVIDER_NOT_CONFIGURED"

    def fetch_items(self) -> list[object]:
        return []

    def normalize_item(self, item: object) -> NormalizedPosItem:
        raise NotImplementedError("GENERIC_POS_NORMALIZATION_NOT_IMPLEMENTED")
