from app.services.delivery_provider_service import (
    get_delivery_provider_readiness,
    run_mock_delivery_provider_dry_run,
)
from app.services.external_integration_readiness_service import build_external_integration_readiness
from app.services.notification_provider_service import (
    get_notification_provider_readiness,
    run_mock_notification_provider_dry_run,
)
from app.services.payment_provider_service import (
    get_payment_provider_readiness,
    run_mock_payment_provider_dry_run,
)
from app.services.pos_provider_service import get_pos_provider_readiness, run_mock_pos_provider_dry_run


def _assert_no_external_calls(items: list[object]) -> None:
    for item in items:
        assert item.external_calls_enabled is False, f"{item} unexpectedly enabled external calls"


def test_payment_provider_readiness_keeps_mock_and_skeleton_external_calls_disabled() -> None:
    readiness = get_payment_provider_readiness()

    assert {item.provider for item in readiness} >= {"MOCK", "TOSS"}
    assert next(item for item in readiness if item.provider == "MOCK").status == "READY"
    assert next(item for item in readiness if item.provider == "TOSS").status == "NOT_ENABLED"
    _assert_no_external_calls(readiness)


def test_payment_provider_mock_dry_run_confirms_without_external_pg_calls() -> None:
    result = run_mock_payment_provider_dry_run()

    assert result.provider == "MOCK"
    assert result.ready_status == "READY"
    assert result.confirm_status == "PAID"
    assert result.external_calls_enabled is False
    assert "No external PG API calls" in result.message


def test_delivery_provider_readiness_keeps_mock_and_noop_external_calls_disabled() -> None:
    readiness = get_delivery_provider_readiness()

    assert {item.provider for item in readiness} >= {"MOCK_DELIVERY", "NOOP_DELIVERY"}
    assert next(item for item in readiness if item.provider == "MOCK_DELIVERY").status == "READY"
    assert next(item for item in readiness if item.provider == "NOOP_DELIVERY").status == "NOT_ENABLED"
    _assert_no_external_calls(readiness)


def test_delivery_provider_mock_dry_run_creates_without_external_delivery_calls() -> None:
    result = run_mock_delivery_provider_dry_run()

    assert result.provider == "MOCK_DELIVERY"
    assert result.readiness_status == "READY"
    assert result.create_status == "REQUESTED"
    assert result.external_calls_enabled is False
    assert "No external delivery API calls" in result.message


def test_notification_provider_readiness_keeps_mock_and_noop_external_calls_disabled() -> None:
    readiness = get_notification_provider_readiness()

    assert {item.provider for item in readiness} >= {"IN_APP_MOCK", "NOOP_EXTERNAL_NOTIFICATION"}
    assert next(item for item in readiness if item.provider == "IN_APP_MOCK").status == "READY"
    assert next(item for item in readiness if item.provider == "NOOP_EXTERNAL_NOTIFICATION").status == "NOT_ENABLED"
    _assert_no_external_calls(readiness)


def test_notification_provider_mock_dry_run_sends_without_external_notification_calls() -> None:
    result = run_mock_notification_provider_dry_run()

    assert result.provider == "IN_APP_MOCK"
    assert result.readiness_status == "READY"
    assert result.delivered is True
    assert result.skipped is False
    assert result.external_calls_enabled is False
    assert "No Email/Kakao/Push/Slack/Webhook calls" in result.message


def test_pos_provider_readiness_keeps_mock_and_generic_noop_external_calls_disabled() -> None:
    readiness = get_pos_provider_readiness()

    assert {item.provider for item in readiness} >= {"MOCK_POS", "GENERIC_POS"}
    assert next(item for item in readiness if item.provider == "MOCK_POS").status == "READY"
    assert next(item for item in readiness if item.provider == "GENERIC_POS").status == "NOT_CONFIGURED"
    _assert_no_external_calls(readiness)


def test_pos_provider_mock_dry_run_syncs_without_external_pos_calls() -> None:
    result = run_mock_pos_provider_dry_run()

    assert result.provider == "MOCK_POS"
    assert result.readiness_status == "READY"
    assert result.normalized_item_count >= 1
    assert result.external_calls_enabled is False
    assert "No external POS API calls" in result.message


def test_external_integration_readiness_summary_reports_mock_ready_without_external_calls() -> None:
    summary = build_external_integration_readiness()

    assert summary.overall_status == "MOCK_READY"
    assert summary.external_calls_enabled is False
    assert {item.area for item in summary.items} == {"PAYMENT", "DELIVERY", "NOTIFICATION", "POS"}
    assert {item.area for item in summary.dry_runs} == {"PAYMENT", "DELIVERY", "NOTIFICATION", "POS"}
    _assert_no_external_calls(summary.items)
    _assert_no_external_calls(summary.dry_runs)

