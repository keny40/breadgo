from decimal import Decimal

from app.services.delivery_provider.base import (
    DeliveryCreateResult,
    DeliveryProviderReadiness,
    DeliveryQuoteRequest,
    DeliveryQuoteResult,
)


class MockDeliveryProvider:
    provider_name = "MOCK_DELIVERY"

    def validate_connection(self) -> DeliveryProviderReadiness:
        return DeliveryProviderReadiness(
            provider=self.provider_name,
            status="READY",
            mode="MOCK_ONLY",
            external_calls_enabled=False,
            message="Mock delivery provider is available. No external delivery API calls are performed.",
        )

    def quote_delivery(self, request: DeliveryQuoteRequest) -> DeliveryQuoteResult:
        fee = Decimal("3000.00") if request.fulfillment_method == "QUICK_DELIVERY" else Decimal("2500.00")
        return DeliveryQuoteResult(
            provider=self.provider_name,
            fulfillment_method=request.fulfillment_method,
            delivery_fee=fee,
            external_calls_enabled=False,
            message="Mock delivery quote generated without external provider calls.",
        )

    def create_delivery(self, request: DeliveryQuoteRequest) -> DeliveryCreateResult:
        return DeliveryCreateResult(
            provider=self.provider_name,
            delivery_status="REQUESTED",
            external_delivery_id="mock-delivery-not-sent",
            external_calls_enabled=False,
            message="Mock delivery request recorded as dry-run only. No external provider calls were performed.",
        )

    def cancel_delivery(self, external_delivery_id: str) -> DeliveryCreateResult:
        return DeliveryCreateResult(
            provider=self.provider_name,
            delivery_status="CANCELLED",
            external_delivery_id=external_delivery_id,
            external_calls_enabled=False,
            message="Mock delivery cancellation completed without external provider calls.",
        )
