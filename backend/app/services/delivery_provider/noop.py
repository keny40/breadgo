from decimal import Decimal

from app.services.delivery_provider.base import (
    DeliveryCreateResult,
    DeliveryProviderReadiness,
    DeliveryQuoteRequest,
    DeliveryQuoteResult,
)


class NoopDeliveryProvider:
    provider_name = "NOOP_DELIVERY"

    def validate_connection(self) -> DeliveryProviderReadiness:
        return DeliveryProviderReadiness(
            provider=self.provider_name,
            status="NOT_ENABLED",
            mode="NOOP_ONLY",
            external_calls_enabled=False,
            message="Noop delivery provider is intentionally disabled. No external delivery API calls are performed.",
        )

    def quote_delivery(self, request: DeliveryQuoteRequest) -> DeliveryQuoteResult:
        return DeliveryQuoteResult(
            provider=self.provider_name,
            fulfillment_method=request.fulfillment_method,
            delivery_fee=Decimal("0.00"),
            external_calls_enabled=False,
            message="Noop delivery quote skipped because real delivery integration is not enabled.",
        )

    def create_delivery(self, request: DeliveryQuoteRequest) -> DeliveryCreateResult:
        return DeliveryCreateResult(
            provider=self.provider_name,
            delivery_status="SKIPPED",
            external_delivery_id=None,
            external_calls_enabled=False,
            message="Noop delivery create skipped because real delivery integration is not enabled.",
        )

    def cancel_delivery(self, external_delivery_id: str) -> DeliveryCreateResult:
        return DeliveryCreateResult(
            provider=self.provider_name,
            delivery_status="SKIPPED",
            external_delivery_id=external_delivery_id,
            external_calls_enabled=False,
            message="Noop delivery cancel skipped because real delivery integration is not enabled.",
        )
